package ch.swisstph.expcreator.sweeps;

import java.io.File;
import java.io.Writer;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;

import org.w3c.dom.Document;

import ch.swisstph.expcreator.CombineSweeps;
import ch.swisstph.expcreator.arms.Arm;
import ch.swisstph.expcreator.patchtree.PTBase;

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
    public abstract void writePatches(File parentOutDir) throws Exception;
    
    public Document applyArm(Document document, int index) throws Exception {
        return arms.get(index).apply(document);
    }
    
    

}
