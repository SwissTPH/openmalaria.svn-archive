package ch.swisstph.expcreator.sweeps;

import java.io.File;
import java.sql.Connection;
import java.util.ArrayList;

import org.w3c.dom.Element;

import ch.swisstph.expcreator.CombineSweeps;
import ch.swisstph.expcreator.arms.Arm;
import ch.swisstph.expcreator.arms.ArmTxt;
import ch.swisstph.expcreator.patchtree.PTBase;

public class SweepTxt extends Sweep {

	public SweepTxt(String fName,File[] armTxts) throws Exception {
		
		super(fName);
		
		System.out.println("SweepTxt: " + name);
		
		Element base = CombineSweeps.getBaseElement();
		
		arms = new ArrayList<Arm>(armTxts.length);
		
		for (int i = 0; i < armTxts.length; ++i) {
            arms.add(new ArmTxt(base, armTxts[i]));
            String armName = arms.get(i).getName();
            if (armName.equals("comparator")) {
                if (refArm != -1) {
                    System.out.println("Sweep " + name + ": multiple reference arms (reference.xml/comparator.xml/base.xml)!");
                    throw new RuntimeException("multiple reference arms");
                }
                refArm = cmpArm = i;
                System.out.print("\t[reference and comparator]");
            } else if (armName.equals("reference") || armName.equals("base")) {
                if (refArm != -1) {
                    System.out.println("Sweep " + name + ": multiple reference arms (reference.xml/comparator.xml/base.xml)!");
                    throw new RuntimeException("multiple reference arms");
                }
                refArm = i;
                System.out.print("\t[reference]");
            }
            System.out.println();
        }
	}

	public void updateDb(Connection conn, int sweepIndex) throws Exception {}

	public void writePatches(File parentOutDir) throws Exception {}

	public PTBase getPatchCoverage() {
		return null;
	}

}
