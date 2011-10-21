package ch.swisstph.expcreator.sweeps;

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

import java.io.File;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;

import javax.xml.transform.dom.DOMSource;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.xml.sax.SAXException;

import ch.swisstph.expcreator.CombineSweeps;
import ch.swisstph.expcreator.arms.Arm;
import ch.swisstph.expcreator.arms.ArmXml;
import ch.swisstph.expcreator.patchtree.PTBase;
import ch.swisstph.expcreator.utils.Utils;

/**
 * A Sweep represents one set of changes (Arms), one of which must be chosen for
 * each scenario.
 */
public class SweepXml extends Sweep {

    // Construct sweep with name fName and arms read from armXmls
    public SweepXml(String fName, File[] armXmls) throws Exception {

        super(fName);

        System.out.println("SweepXml: " + name);

        Element base = CombineSweeps.getBaseElement();

        for (int i = 0; i < armXmls.length; ++i) {
            File file = armXmls[i];
            if (file.getName().equals("base.xml")
                    || file.getName().endsWith("comparatorBase.xml")) {
                // Sweep has its own base to compare against.
                if (file.getName().endsWith("comparatorBase.xml")) {
                    cmpArm = i;
                }
                Document baseDoc = CombineSweeps.getBuilder().parse(file);
                base = baseDoc.getDocumentElement();
                base.setAttribute("name", ""); // make sure this Attr isn't
                                               // patched

                if (!CombineSweeps.getBaseElement().getNodeName()
                        .equals(base.getNodeName())) {
                    System.out.println("root element name differs: "
                            + CombineSweeps.getBaseElement().getNodeName()
                            + ", " + base.getNodeName());
                    throw new RuntimeException("root element name mismatch");
                }

                // Reformat: remove all whitespace nodes
                Utils.stripWhitespace(base, org.w3c.dom.Node.TEXT_NODE, "#text");
                baseDoc.normalize();

                try {
                    if (CombineSweeps.getValidator() != null)
                        CombineSweeps.getValidator().validate(
                                new DOMSource(CombineSweeps.getBaseDocument()));
                } catch (SAXException e) {
                    System.out.println("Validation error reading "
                            + file.getName() + ":");
                    System.out.println(e.getMessage());
                    throw new RuntimeException("validation failure");
                }

                break; // won't be more than one
            }
        }

        arms = new ArrayList<Arm>(armXmls.length);

        for (int i = 0; i < armXmls.length; ++i) {
            arms.add(new ArmXml(base, armXmls[i]));
            String armName = arms.get(i).getName();
            if (armName.equals("comparator")) {
                if (refArm != -1) {
                    System.out
                            .println("Sweep "
                                    + name
                                    + ": multiple reference arms (reference.xml/comparator.xml/base.xml)!");
                    throw new RuntimeException("multiple reference arms");
                }
                refArm = cmpArm = i;
                System.out.print("\t[reference and comparator]");
            } else if (armName.equals("reference") || armName.equals("base")
                    || armName.endsWith("comparatorBase")) {
                if (refArm != -1) {
                    System.out
                            .println("Sweep "
                                    + name
                                    + ": multiple reference arms (reference.xml/comparator.xml/base.xml)!");
                    throw new RuntimeException("multiple reference arms");
                }
                refArm = i;
                System.out.print("\t[reference]");
            }
            System.out.println();
        }

        if (refArm == -1) {
            System.out
                    .println("Warning: no reference specified — using first arm as reference.");
            refArm = 0; // use only arm
        }
    }

    // Construct sweep with name fName and arms from nSeeds different seeds
    public SweepXml(String fName, int nSeeds) throws Exception {
        super(fName);

        if (nSeeds < 1) {
            System.out.println("--seeds: must have at least one seed");
            throw new RuntimeException("commandline error");
        }

        System.out.println("Sweep: " + name);
        System.out.println("Arms:\t1-" + nSeeds);

        arms = new ArrayList<Arm>(nSeeds);

        for (int i = 1; i <= nSeeds; ++i) { // first seed should be 1
            arms.add(new ArmXml(i));
        }

        refArm = 0; // not very meaningful but must be something
    }

    public PTBase getPatchCoverage() {
        PTBase cov = null;
        for (Arm arm : arms) {
            cov = PTBase.union(cov, ((ArmXml) arm).getPatchCoverage());
        }
        return cov;
    }

    public void updateDb(Connection conn, int sweepIndex) throws Exception {
        Statement stmt = conn.createStatement();
        // Need to disable foreign-key checks while inserting cross-reference:
        stmt.execute("SET FOREIGN_KEY_CHECKS = 0");

        // sweeps TABLE: exp_id, swe_id(auto key), name, ref_arm_id, s_group
        // Names sweeps, and details their sweep group and reference arm
        String sql = "INSERT INTO sweeps (exp_id,name,ref_arm_id,s_group) VALUES (?,?,?,?)";
        PreparedStatement pstmt = conn.prepareStatement(sql,
                Statement.RETURN_GENERATED_KEYS);
        pstmt.setInt(1, CombineSweeps.getExpId());
        pstmt.setString(2, name);
        pstmt.setInt(3, 0); // don't have correct ref until we've inserted arms
        pstmt.setInt(4, sweepIndex); // always use a unique sweep group (fully
                                     // factorial design)
        pstmt.executeUpdate();
        ResultSet rs = pstmt.getGeneratedKeys();
        if (rs.next()) {
            id = rs.getInt(1); // get generated ID
        } else {
            System.out.println("DB error: unable to get generated key");
            throw new RuntimeException("unable to get generated key");
        }

        for (int i = 0; i < arms.size(); ++i) {
            arms.get(i).updateDb(conn, id, i == cmpArm);
        }

        stmt.execute("UPDATE sweeps SET ref_arm_id="
                + Integer.toString(arms.get(refArm).getId()) + " WHERE swe_id="
                + Integer.toString(id));
        stmt.execute("SET FOREIGN_KEY_CHECKS = 1");
    }

    public void writePatches(File parentOutDir) throws Exception {
        File outDir = new File(parentOutDir, name);
        outDir.mkdir();

        for (Arm arm : arms) {
            arm.writePatch(outDir);
        }
    }

}
