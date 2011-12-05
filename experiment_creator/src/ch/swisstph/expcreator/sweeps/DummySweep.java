package ch.swisstph.expcreator.sweeps;

import java.io.File;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;

import ch.swisstph.expcreator.CombineSweeps;
import ch.swisstph.expcreator.arms.Arm;
import ch.swisstph.expcreator.arms.DummyArm;
import ch.swisstph.expcreator.patchtree.PTBase;

public class DummySweep extends Sweep {

    public DummySweep(String fName) throws Exception {
        super(fName);
        arms = new ArrayList<Arm>(1);
        arms.add(new DummyArm(fName));
        refArm = 0;
    }

    public PTBase getPatchCoverage() {
        return null;
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
    }
}
