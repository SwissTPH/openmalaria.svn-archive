/**
 * experiment_creator: An experiment creation tool for openmalaria
 * Copyright (C) 2005-2011 Swiss Tropical Institute and Liverpool School Of Tropical Medicine
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
import com.swisstph.expcreator.CombineSweeps;

public class ExpcreatorStandalone {
	
	public static void main(String[] args) {
        ClassLoader.getSystemClassLoader().setDefaultAssertionStatus(true);

        String inputPath = null, outputPath = null;
        String scnListPath = null;
        int nSeeds = -1;
        boolean uniqueSeeds = true;
        boolean patches = false, doValidation = true;
        String expName = "EXPERIMENT";
        int sceIdStart = 0;
        String expDescription = null;
        String dbUrl = null, dbUser = null;

        for (int i = 0; i < args.length; i++) {
            if (args[i].startsWith("--")) {
                if (args[i].equals("--stddirs")) {
                    if( inputPath==null && outputPath==null && scnListPath==null ){
                        String basePath=args[++i];
                        inputPath=basePath+File.separator+"description";
                        outputPath=basePath+File.separator+"scenarios";
                        File outp=new File(outputPath);
                        if( !outp.isDirectory() ){
                            // Not a directory
                            if( !outp.mkdir() ){        // presumably something else (exception on permission error?)
                                System.err.println( "Error: unable to create "+outputPath );
                                System.exit(1);
                            }
                        }
                        scnListPath=basePath+File.separator+"scenarios.csv";
                    }
                    else
                    {
                        printHelp();
                    }
                } else if (args[i].equals("--seeds")) {
                        nSeeds = Integer.parseInt(args[ ++i ] );
                } else if( args[i].equals( "--unique-seeds")) {
                    uniqueSeeds = Boolean.parseBoolean(args[ ++i ]);
                } else if( args[i].equals( "--patches")) {
                    patches = true;
                } else if( args[i].equals( "--no-validation")) {
                	doValidation = false;
                } else if (args[i].equals("--name")) {
                	expName = args[ ++i ];
                } else if (args[i].equals("--sce-ID-start")) {
                	sceIdStart = Integer.parseInt(args[ ++i ]);
                } else if (args[i].equals("--desc")) {
                    expDescription = args[ ++i ];
                } else if( args[i].equals( "--db")) {
                    dbUrl = args[ ++i ];
                } else if( args[i].equals( "--dbuser")) {
                    dbUser = args[ ++i ];
                } else {
                	System.out.println( "Unrecognised option: "+args[i] );
                    printHelp();
                }
            } else {
                if (inputPath == null) {
                    inputPath = args[i];
                } else if (outputPath == null) {
                    outputPath = args[i];
                } else {
                    printHelp();
                }
            }
        }

        if (inputPath == null || outputPath == null) {
            System.out.println("Required arguments: INPUT_DIR OUTPUT_DIR");
            printHelp();
        }
        if (dbUrl == null ){	// non-DB mode
        }
        else
        {	// DB mode
        	if ( expDescription == null || dbUser == null ) {
        			System.out.println("--db requires --dbuser and --desc arguments");
        			printHelp();
        	}
        	if( !expName.equals("EXPERIMENT") || sceIdStart != 0 ){
        		System.out.println("--name and --sce-ID-start cannot be used in DB mode");
        		printHelp();
        	}
        }

        CombineSweeps mainObj = new CombineSweeps(expName, expDescription);

        try {
            // Find all sweeps
            mainObj.readSweeps(inputPath, doValidation);

            if (nSeeds >= 0) {
                mainObj.addSeedsSweep(nSeeds);
            }

            mainObj.sweepChecks();

            if (patches) {
                mainObj.writePatches(outputPath);
            } else {
                File outputDir = mainObj.genCombinationList(sceIdStart, outputPath);

                if (dbUrl != null) {
                    if (mainObj.updateDb(dbUrl, dbUser)) {
                        System.out.println("Database connection error.");
                        System.exit(1);
                    }
                }

                mainObj.combine(outputDir, uniqueSeeds, scnListPath);
            }
        } catch (RuntimeException e) {
            System.out.println("Exception: " + e.getMessage());
            e.printStackTrace(System.out);
            System.exit(1);
        } catch (Exception e) {
            e.printStackTrace(System.out);
            System.exit(1);
        }
    // Done.
    }

    public static void printHelp() {
        System.out.println(
	    "Usage:\n"
	    + "\tCombineSweeps [options] INPUT_DIR OUTPUT_DIR\n"
        + "\tCombineSweeps --stddirs PATH [options]\n"
	    + "\n"
	    + "Options:\n"
        + "  --stddirs PATH\tAssume a standard setup: INPUT_DIR is PATH/description,\n"
        + "                 OUTPUT_DIR is PATH/scenarios, and a list of what the\n"
        + "                 scenarios are is written to PATH/scenarios.csv\n"
        + "  --seeds N		Add a sweep of N random seeds\n"
	    + "  --unique-seeds B	If B is true (default), give every scenario a unique seed\n"
	    + "  --patches		Write out arms as patches instead of resulting\n"
	    + "			combined XML files. (Currently broken.)\n"
	    + "  --no-validation		Turn off validation.\n"
	    + "\n"
	    + "Non-DB mode options:\n"
	    + "  --name NAME		Name of experiment; for use when not in DB mode.\n"
	    + "  --sce-ID-start J	Enumerate the output scenarios starting from J instead\n"
	    + "			of 0 (in DB mode numbers come from DB).\n"
	    + "\n"
	    + "DB-mode options:\n"
	    + "  --db jdbc:mysql://SERVER:3306/DATABASE\n"
	    + "			Enable DB mode: read and update DATABASE at address SERVER.\n"
	    + "  --dbuser USER		Log in as USER. Password will be read from command prompt.\n"
	    + "  --desc DESC		Enter a description for database update.\n"
	    + "\n"
	    + "INPUT_DIR should contain one XML file named base.xml and a set of\n"
	    + "sub-directories. Each sub-directory containing any XML files is\n"
	    + "considered a sweep. Each XML file within each sweep's directory is\n"
	    + "considered an arm. See comment at the top of CombineSweeps.java\n"
	    + "for more information.\n"
	    + "\n"
	    + "Error and status messages are printed to stdout, and a list of created\n"
	    + "scenario files to stderr (which you may wish to redirect: 2>scenarios.txt).\n"
	    + "\n"
	    + "TODO: some mechanism for substituting variables, such as vaccine efficacy.\n"
        );
        System.exit(1);
    }

}
