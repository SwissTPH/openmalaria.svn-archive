package com.swisstph.expcreator.sweeps;

import java.io.File;
import java.io.PrintStream;
import java.io.Writer;
import java.sql.Connection;
import java.util.ArrayList;

import org.w3c.dom.Document;

import com.swisstph.expcreator.arms.Arm;
import com.swisstph.expcreator.patchtree.PTBase;

public abstract class Sweep {

	protected int id = -1;
	protected final String name;
	protected ArrayList<Arm> arms;
	protected int refArm = -1,  cmpArm = -1;
	
	 public Sweep(String fName) throws Exception {
		 this.name = fName;
	 };
	 
	public int getId() {
		return id;
	}

	public String getName() {
		return name;
	}

	public int getArmId(int armIndex) {
		return arms.get(armIndex).getId();
	}

	public int getLength() {
		return arms.size();
	}
	// Returns index of comparator arm, or -1 if no comparator.
	public int getComparator() {
		return cmpArm;
	}
	
    public void writeName(Writer w, int index) throws Exception {
        String armName = arms.get(index).getName();
        w.append(",").append(armName);
    }
    
    public void writeNamePair(Writer w, int index) throws Exception {
        String armName = arms.get(index).getName();
        w.append(",").append(name).append(":").append(armName);
    }
    
    public abstract PTBase getPatchCoverage();
    public abstract void updateDb(Connection conn, int sweepIndex) throws Exception;
    public abstract void writePatches(File parentOutDir) throws Exception;
    
    public Document applyArm(Document document, int index) throws Exception {
        return arms.get(index).apply(document);
    }
    
    

}
