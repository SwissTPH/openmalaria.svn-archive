package ch.swisstph.expcreator;

/**
 * experiment_creator: An experiment creation tool for openmalaria
 * Copyright (C) 2005-2010 Swiss Tropical Institute and Liverpool School Of Tropical Medicine
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.*/

// Troubleshooting:
// The database connection/update part needs the MySQL JDBC driver installed
// (debian package: libmysql-java).
// Needs to be run with the correct classpath (java -cp .:/usr/share/java/mysql.jar ExpcreatorStandalone ...)
// On debian, this bug hit me: http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=560044
import java.util.*;
import java.io.*;
import javax.xml.parsers.*;
import javax.xml.transform.*;
import javax.xml.transform.dom.*;
import javax.xml.transform.stream.StreamResult;
import javax.xml.validation.*;
import java.sql.*;

import org.w3c.dom.*;
import org.xml.sax.SAXException;

import ch.swisstph.expcreator.ScenarioArmAssociation;
import ch.swisstph.expcreator.exceptions.PatchConflictException;
import ch.swisstph.expcreator.patchtree.PTBase;
import ch.swisstph.expcreator.sweeps.DummySweep;
import ch.swisstph.expcreator.sweeps.Sweep;
import ch.swisstph.expcreator.sweeps.SweepTxt;
import ch.swisstph.expcreator.sweeps.SweepXml;
import ch.swisstph.expcreator.utils.TXTFileFilter;
import ch.swisstph.expcreator.utils.Utils;
import ch.swisstph.expcreator.utils.XMLFileFilter;

/**
 * A tool to exponentially combine sweeps.
 * 
 * An experiment should be composed of a base scenario and a set of sweeps. Each
 * sweep should be composed of a set of arms. Each arm should be a scenario
 * differing from the base in some way.
 * 
 * An experiment is described as a directory structure. It must contain a base
 * scenario named 'base.xml' and can have any number of directories containing
 * XML files, each directory representing a sweep. (Other files and directories
 * not containing .xml files are ignored.)
 * 
 * For example, given an input directory 'experiment':
 * 
 * experiment -> base.xml -> readme.txt -> popSize -> -> 10000.xml ->
 * interventions -> -> comparator.xml -> -> 50perc.xml -> -> 100perc.xml
 * 
 * the directory 'popSize' represents a sweep (named 'popSize') with a single
 * arm '10000' (setting the preferred population size in all scenarios), and the
 * directory 'interventions' represents a sweep with a base-case and two
 * coverage levels. 'base.xml' is used as the base scenario and 'readme.txt' is
 * ignored.
 * 
 * Sweeps are described by directories containing XML files. Each XML file
 * describes one arm. Each sweep needs a reference arm and reference arms can
 * potentially be a comparator. If a file called "reference.xml",
 * "comparator.xml" or "base.xml" exists this becomes the sweep's reference
 * (there can only be one of these). If none exist, an arbitrary arm is chosen
 * as the reference arm. If "comparator.xml" exists, it also becomes a
 * comparator (i.e. this arm of this sweep is always chosen when looking for a
 * comparator scenario for any given scenario).
 * 
 * Arms are described as a complete XML file. Its differences from the base.xml
 * file describe the effect of the arm (these are converted to a patch, which is
 * applied against copies of the base scenario). Usually, these differences are
 * taken against the experiment's base.xml file, however, if the sweep also has
 * a base.xml file, patches are generated from the differences to this file.
 * This can be useful when, for example, a sweep of models is copied from
 * another source and it is not desired to update each arm to have the correct
 * differences to the experiment's base.xml; however, it should be used
 * carefully.
 * 
 * Additionally, each arm needs a label (used in plots). Arm labels are taken
 * from the scenario element's "name" attribute, while the arm's name is taken
 * from the file name.
 * 
 * An experiment can then factorially combined by taking all possible
 * combinations of one arm from each sweep, and in each case patching the arms'
 * diffs into the base scenario.
 * 
 * For ease of use, an extra sweep of N random seeds can be added with the
 * --seeds command-line option.
 *********************************************************************/
public class CombineSweeps {

    private static FilenameFilter xmlFilter;
    private static FilenameFilter txtFilter;
    private static Transformer transformer;
    private static DocumentBuilder builder;
    private static Document baseDocument;
    private static Element baseElement;
    private static Validator validator;

    // Identifies the experiment; with database access is next free number but
    // otherwise is "EXPERIMENT"
    private static int expId;
    private static String expName;
    // Description; only used for DB update
    private String expDescription;
    private ArrayList<Sweep> sweeps;
    private boolean min3Sweeps;
    private ScenarioArmAssociation[] scenarios;

    public CombineSweeps(String name, String desc, boolean min3Sweeps) {
        expId = -1;
        expName = name;
        expDescription = desc;
        this.min3Sweeps = min3Sweeps;
    }

    // Generate a Sweep from a directory if it contains XML files.
    public void readSweep(File dir) throws Exception {
        if (!dir.isDirectory()) {
            return;
        }

        File[] xmlFiles = dir.listFiles(xmlFilter);
        if (xmlFiles.length != 0) {
            Sweep sweep = new SweepXml(dir.getName(), xmlFiles);
            sweeps.add(sweep);
        }

        File[] txtFiles = dir.listFiles(txtFilter);
        if (txtFiles.length != 0) {
            Sweep sweep = new SweepTxt(dir.getName(), txtFiles);
            sweeps.add(sweep);
        }
    }

    public void readSweeps(String inputPath, boolean validation)
            throws Exception {
        xmlFilter = new XMLFileFilter(false);
        txtFilter = new TXTFileFilter();

        DocumentBuilderFactory fact = DocumentBuilderFactory.newInstance();
        fact.setNamespaceAware(true);
        builder = fact.newDocumentBuilder();
        sweeps = new ArrayList<Sweep>();

        File inputDir = new File(inputPath);
        if (!inputDir.isDirectory()) {
            System.out.println("Require input directory: " + inputPath);
            System.exit(1);
        }

        // Read base XML file
        File[] baseXMLs = inputDir.listFiles(new XMLFileFilter(true));
        if (baseXMLs.length != 1) {
            System.out.println("Expected base.xml file in " + inputPath);
            System.exit(1);
        }
        baseDocument = builder.parse(baseXMLs[0]);
        baseElement = baseDocument.getDocumentElement();
        baseElement.setAttribute("name", ""); // make sure this Attr isn't
                                              // patched

        // Reformat: remove all whitespace nodes
        Utils.stripWhitespace(baseElement, org.w3c.dom.Node.TEXT_NODE, "#text");
        baseDocument.normalize();

        if (validation) {
            // Create a validator for use later
            String schemaName = baseElement
                    .getAttribute("xsi:noNamespaceSchemaLocation");

            File xsdFile = new File(inputDir, schemaName);
            if (!xsdFile.isFile()) {
                System.out.println("Unable to find schema "
                        + xsdFile.getCanonicalPath()
                        + "; required for validation.");
                throw new RuntimeException("schema not found");
            }

            SchemaFactory factory = SchemaFactory
                    .newInstance("http://www.w3.org/2001/XMLSchema");
            Schema schema = factory.newSchema(xsdFile);
            validator = schema.newValidator();

            try {
                validator.validate(new DOMSource(baseDocument));
            } catch (SAXException e) {
                System.out.println("While reading: " + baseXMLs[0].getName());
                System.out.println(e.getMessage());
                throw new RuntimeException("validation failure");
            }
        }

        // Read sweeps & arms
        for (File subdir : inputDir.listFiles()) {
            readSweep(subdir);
        }
        if (min3Sweeps) {
            while (sweeps.size() < 3) {
                sweeps.add(new DummySweep("dummy" + (sweeps.size() + 1)));
            }

        }
    }

    /**
     * Experiment checks/statistics.
     * 
     * Sort sweeps such that a sweep may not change an element or attribute
     * affected by a previous sweep, unless the effect in the previous sweep was
     * invariant (TODO). Complain if there is any other patch conflict.
     * 
     * Check whether survey times and monitoring age-groups are invariant across
     * scenarios. If they are, output data into auxilliary files.
     * 
     * Print the total number of scenarios.
     */
    public void sweepChecks() {
        PTBase unionOfPatches = null;
        int nScenarios = 1;
        for (Sweep sweep : sweeps) {

            if (sweep instanceof SweepXml) {
                PTBase cov = sweep.getPatchCoverage();
                try {
                    PTBase.checkConflicts(unionOfPatches, cov);
                } catch (PatchConflictException e) {
                    System.out.println("Conflict in sweep " + sweep.getName());
                    System.out.println(e.getMessage());
                    throw new RuntimeException("patch conflict");
                }
                unionOfPatches = PTBase.union(unionOfPatches, cov);
                nScenarios *= sweep.getLength();
            } else if (sweep instanceof SweepTxt) {
                nScenarios *= sweep.getLength();
            }

        }
        // TODO: sort and allow clashes where elements are invariant in all but
        // one case

        System.out.println(Integer.toString(nScenarios)
                + " scenarios in experiment.");

        // TODO: get survey times and age groups elements
        // like this?: Node scenario = PTBase.getChildNodes (cov,
        // "scenario").get(0);
    }

    /**
     * Create a list of all combinations of arms and write it to a file.
     * 
     * sceIdStart: number to start numerating scenarios from (usually 0)
     * 
     * scnListPath: path of file to write list of scenarios to
     * 
     * readList: if true, the scnListPath file is read from instead of written
     * to, and scenarios corresponding to lines in the file are generated. File
     * must not be reordered or reformatted other than the deletion of lines.
     */
    public void genCombinationList(int sceIdStart, String scnListPath,
            boolean readList) throws Exception {
        int combinations = 1;
        int[] lengths = new int[sweeps.size()];
        for (int i = 0; i < lengths.length; ++i) {
            lengths[i] = sweeps.get(i).getLength();
            combinations *= lengths[i];
        }

        scenarios = new ScenarioArmAssociation[combinations];

        int idCounter = sceIdStart;
        for (int c = 0; c < combinations; ++c) {
            scenarios[c] = new ScenarioArmAssociation(c, idCounter, lengths);
            idCounter += 1;
        }

        if (!readList) {
            PrintStream scnListOut = System.err;
            if (scnListPath != null) {
                OutputStream fout = new FileOutputStream(scnListPath);
                OutputStream bout = new BufferedOutputStream(fout);
                scnListOut = new PrintStream(bout);
            }
            scnListOut.print("file");
            for (Sweep sweep : sweeps) {
                scnListOut.print(",");
                scnListOut.print(sweep.getName());
            }
            scnListOut.println();

            PrintWriter pw = new PrintWriter(scnListOut);
            for (int c = 0; c < scenarios.length; ++c) {
                scenarios[c].writeDescription(pw, sweeps);
                pw.println();
            }
            pw.flush();

            if (scnListOut != System.err) {
                scnListOut.flush();
                scnListOut.close();
            }
        } else/* read from file */{
            final FileReader fr = new FileReader(scnListPath);
            final BufferedReader br = new BufferedReader(fr, 24576 /*
                                                                    * 24K chars
                                                                    * (48K
                                                                    * bytes),
                                                                    * 75% of
                                                                    * allocation
                                                                    * is optimal
                                                                    */);

            String line = br.readLine();
            if (line == null) {
                System.out.println("expected a list of scenarios in: "
                        + scnListPath);
                throw new RuntimeException("file not found");
            }
            StringWriter headerW = new StringWriter(256);
            headerW.append("file");
            for (Sweep sweep : sweeps) {
                headerW.append(",");
                headerW.append(sweep.getName());
            }
            if (!line.equals(headerW.toString())) {
                System.out.println("Error: in " + scnListPath
                        + " expected header:");
                System.out.println("\t" + headerW.toString());
                System.out.println("not:\t" + line);
                throw new RuntimeException("incompatible header");
            }

            line = br.readLine();
            for (int c = 0; c < scenarios.length; ++c) {
                if (line != null) {
                    StringWriter lineW = new StringWriter(256);
                    scenarios[c].writeDescription(new PrintWriter(lineW),
                            sweeps);
                    if (line.equals(lineW.toString())) {
                        line = br.readLine();
                        continue; // don't set scenarios[c] to null
                    }
                }
                scenarios[c] = null;
            }

            if (line != null) {
                System.out
                        .println("Error: file has lines not matching an arm combination (or in the wrong order):");
                int c = 0;
                while (line != null) {
                    if (c > 10) {
                        System.out.println("...");
                        break;
                    }
                    c += 1;
                    System.out.println(line);
                    line = br.readLine();
                }
                throw new RuntimeException("unmatched lines in scenario list");
            }

            br.close();
        }
    }

    /**
     * Gets IDs from database and enters new experiment data.
     * 
     * Throws on failure.
     */
    public void updateDb(String dbUrl, String dbUser) throws Exception {
        if (expDescription == null) {
            throw new RuntimeException("DESC required for DB update");
        }

        Class.forName("com.mysql.jdbc.Driver");
        Connection conn = null;

        if (dbUser == null) {
            System.out.println("Attempting anonymous connection to " + dbUrl);
            conn = DriverManager.getConnection(dbUrl);
        } else {
            System.out.println("Attempting connection to " + dbUrl + " as "
                    + dbUser);
            // Get password
            Console cons = System.console();
            if (cons == null) {
                System.out.println("unable to read password from console");
                throw new RuntimeException("console error");
            }
            char[] passwd = cons.readPassword("[%s]", "Password for " + dbUser);
            String dbPwd = new String(passwd); // We need a string. This copies
                                               // password in memory and doesn't
                                               // erase though :(
            java.util.Arrays.fill(passwd, ' '); // erase password from memory
            conn = DriverManager.getConnection(dbUrl, dbUser, dbPwd);
        }

        if (!conn.isClosed()) {
            System.out
                    .println("Successfully connected to MySQL server using TCP/IP...");
        }
        // we only have one transaction; maybe this makes it faster?
        conn.setTransactionIsolation(Connection.TRANSACTION_READ_UNCOMMITTED);
        conn.setAutoCommit(false); // We commit atomically

        try {
            // experiments TABLE: exp_id(auto key), description, flg_active(1)
            // Describes experiments and records key.
            PreparedStatement experimentsSt = conn
                    .prepareStatement(
                            "INSERT INTO experiments (description,flg_active,stu_id) VALUES (?,1,1)",
                            Statement.RETURN_GENERATED_KEYS);
            experimentsSt.setString(1, expDescription);
            experimentsSt.executeUpdate();
            ResultSet rs = experimentsSt.getGeneratedKeys();
            if (rs.next()) {
                expId = rs.getInt(1); // get generated ID
                expName = Integer.toString(expId);
            } else {
                System.out.println("DB error: unable to get generated key");
                throw new RuntimeException("unable to get generated key");
            }
            System.out.println("Inserted into experiments table");

            for (int i = 0; i < sweeps.size(); ++i) {
                // Problem with zero as sweep group id in the visualization
                // software
                // therefore start sweep group ids at one instead of zero
                sweeps.get(i).updateDb(conn, i + 1);
            }
            System.out.println("Inserted into sweeps and arms tables");

            // First pass: insert scenarios & get sce_id
            PreparedStatement scenariosSt = conn
                    .prepareStatement(
                            "INSERT INTO scenarios (exp_id,name,flg_status,cmp_id,css_id) VALUES (?,?,0,0,1)",
                            Statement.RETURN_GENERATED_KEYS);
            scenariosSt.setInt(1, expId);
            for (int i = 0; i < scenarios.length; ++i) {
                if (scenarios[i] != null) {
                    scenarios[i].dbScenarios(scenariosSt);
                }
            }
            System.out.println("Inserted into scenarios table");

            int[] lengths = new int[sweeps.size()];
            for (int i = 0; i < lengths.length; ++i) {
                lengths[i] = sweeps.get(i).getLength();
            }

            PreparedStatement scenarios_sweepsSt = conn
                    .prepareStatement(
                            "INSERT INTO scenarios_sweeps (exp_id,sce_id,swe_id,arm_id) VALUES (?,?,?,?)",
                            Statement.RETURN_GENERATED_KEYS);
            scenarios_sweepsSt.setInt(1, expId);
            for (int i = 0; i < scenarios.length; ++i) {
                if (scenarios[i] != null) {
                    scenarios[i].dbScenariosSweeps(scenarios_sweepsSt, sweeps);
                }
                if (i % 1000 == 0)
                    System.out.println("inserting: " + Integer.toString(i));
            }
            System.out.println("finished dbScenariosSweeps statement");
            scenarios_sweepsSt.executeBatch();
            System.out.println("Inserted into scenarios_sweeps table");

            // Must commit before we can do updates
            conn.commit();

            // Second pass: set cmp_id
            PreparedStatement updateCmpIdSt = conn
                    .prepareStatement("UPDATE scenarios SET cmp_id=? WHERE sce_id=?");
            for (int i = 0; i < scenarios.length; ++i) {
                if (scenarios[i] != null) {
                    scenarios[i].dbUpdateCmpId(updateCmpIdSt, lengths, sweeps,
                            scenarios);
                }
            }
            updateCmpIdSt.executeBatch();
            System.out.println("Updated scenarios table");

            System.out.println("experiment " + expName + ": " + expDescription);
        } catch (Exception e) {
            conn.rollback(); // Failure somewhere: don't want any changes to be
                             // committed
            System.out.println("Error while updating database.");
            throw e;
        } finally {
            if (conn != null) {
                conn.setAutoCommit(true); // OK, now we commit everything
                conn.close();
            }
        }
    }

    public void writePatches(File outputDir) throws Exception {
        transformer = TransformerFactory.newInstance().newTransformer();
        transformer.setOutputProperty(OutputKeys.ENCODING, "UTF-8");
        transformer.setOutputProperty(OutputKeys.METHOD, "xml");
        transformer.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION, "yes");

        for (Sweep sweep : sweeps) {
            sweep.writePatches(outputDir);
        }
    }

    public void combine(File outputDir, boolean uniqueSeeds) throws Exception {
        transformer = TransformerFactory.newInstance().newTransformer();
        transformer.setOutputProperty(OutputKeys.ENCODING, "UTF-8");
        transformer.setOutputProperty(OutputKeys.METHOD, "xml");
        // Add new indentation/new-lines when transforming:
        transformer.setOutputProperty(OutputKeys.INDENT, "yes");
        transformer.setOutputProperty(
                "{http://xml.apache.org/xslt}indent-amount", "2");

        for (int c = 0; c < scenarios.length; ++c) {
            if (scenarios[c] == null) {
                continue;
            }

            // Clone our base
            DOMResult cloneResult = new DOMResult();
            transformer.transform(new DOMSource(baseDocument), cloneResult);
            Document wu = (Document) cloneResult.getNode();
            wu = scenarios[c].applyArms(wu, uniqueSeeds, sweeps);

            // Write out result
            String name = scenarios[c].getFileName();
            File file = new File(outputDir, name);
            FileWriter fileW = new FileWriter(file);
            BufferedWriter out = new BufferedWriter(fileW);
            StreamResult result = new StreamResult(out);
            Source source = new DOMSource(wu);
            transformer.transform(source, result);
            out.close();

            // Validate (after writing so users can find errors in file):
            try {
                if (validator != null) {
                    validator.validate(source);
                }
            } catch (SAXException e) {
                System.out.println("Validation failure in "
                        + file.getCanonicalPath() + ":");
                System.out.println(e.getMessage());
                throw new RuntimeException("validation failure");
            }
        }
    }

    public void addSeedsSweep(int nSeeds) throws Exception {
        Sweep sweep = new SweepXml("seed", nSeeds);
        sweeps.add(sweep);
    }

    public static FilenameFilter getXMLFilter() {
        return xmlFilter;
    }

    public static Transformer getTransformer() {
        return transformer;
    }

    public static DocumentBuilder getBuilder() {
        return builder;
    }

    public static Document getBaseDocument() {
        return baseDocument;
    }

    public static Element getBaseElement() {
        return baseElement;
    }

    public static Validator getValidator() {
        return validator;
    }

    public static int getExpId() {
        return expId;
    }

    public static String getExpName() {
        return expName;
    }

}
