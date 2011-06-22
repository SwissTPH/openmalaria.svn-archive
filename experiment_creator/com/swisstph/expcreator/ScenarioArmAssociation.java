package com.swisstph.expcreator;

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

import java.io.PrintWriter;
import java.io.StringWriter;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;

import org.w3c.dom.Document;
import org.w3c.dom.Element;

import com.swisstph.expcreator.CombineSweeps;
import com.swisstph.expcreator.sweeps.Sweep;
import com.swisstph.expcreator.utils.Utils;


/** One object for each scenario; contains indecies of each arm used. */
public class ScenarioArmAssociation {

    private int sceId;          // database identifier
    private int[] armIndecies;  // An arm index for each sweep (not DB ID)
    private static int uniqueSeed = 1;

    public ScenarioArmAssociation(int n, int id, int[] lengths) {
        sceId = id;     // For now, use this number. If we do DB updates, it will be overwitten.
        armIndecies = new int[lengths.length];

        int div = 1;
        for (int i = 0; i < lengths.length; ++i) {
            armIndecies[i] = (n / div) % lengths[i];
            div *= lengths[i];
        }
    }
    
    public String getFileName() {
        return "wu" + CombineSweeps.getExpName() + "_" + Integer.toString(sceId) + ".xml";
    }

    public void dbScenarios(PreparedStatement pstmt) throws Exception {
        // scenarios TABLE: sce_id(primary key), exp_id, name, flg_status, cmp_id
        // We can't insert the correct cmp_id until our scenarios have the
        // correct (DB) IDs, so we must update cmp_id in a second pass.
        pstmt.setInt(2, sceId); // old ID (scenario number within experiment)
        pstmt.executeUpdate();
        ResultSet rs = pstmt.getGeneratedKeys();
        if (rs.next()) {
            sceId = rs.getInt(1);       // get generated ID
        } else {
            System.out.println("DB error: unable to get generated key");
            throw new RuntimeException("unable to get generated key");
        }
    }

    public void dbScenariosSweeps(PreparedStatement pstmt, ArrayList<Sweep> sweeps) throws Exception {
        // scenarios_sweeps TABLE: ssw_id(auto key), exp_id, sce_id, swe_id, arm_id
        // Maps scenario number sce_id to an arm_id for each sweep swe_id.
        pstmt.setInt(2, sceId);
        for (int i = 0; i < armIndecies.length; ++i) {
            Sweep sweep = sweeps.get(i);
            pstmt.setInt(3, sweep.getId());
            pstmt.setInt(4, sweep.getArmId(armIndecies[i]));
            pstmt.addBatch();
        }
    }

    public void dbUpdateCmpId(PreparedStatement pstmt, int[] lengths, ArrayList<Sweep> sweeps, ScenarioArmAssociation[] scenarios) throws Exception {
        int n = 0;      // index of comparator in scenarios
        int mul = 1;
        for (int i = 0; i < armIndecies.length; ++i) {
            int armIndex = sweeps.get(i).getComparator();       // returns -1 if no comparator
            if (armIndex < 0) {
                armIndex = armIndecies[i];
            }   // use this scenario's arm
            n += armIndex * mul;
            mul *= lengths[i];
        }
        // check n is correct:
        int div = 1;
        for (int i = 0; i < lengths.length; ++i) {
            int armIndex = (n / div) % lengths[i];
            assert (armIndex == sweeps.get(i).getComparator()) || (armIndex == armIndecies[i]);
            div *= lengths[i];
        }

        // Update the comparator now that all scenarios have the correct sceId.
        pstmt.setInt(1, scenarios[n].sceId /* DB ID of comparator */);
        pstmt.setInt(2, sceId);
        pstmt.addBatch();
    }

    public void writeDescription(PrintWriter writer, ArrayList<Sweep> sweeps) throws Exception {
        writer.append(getFileName());
        for (int i = 0; i < armIndecies.length; ++i) {
            sweeps.get(i).writeName(writer, armIndecies[i]);
        }
    }

    public Document applyArms(Document wu,boolean uniqueSeeds,ArrayList<Sweep> sweeps) throws Exception {
        StringWriter wName = new StringWriter(128);
        wName.append(getFileName());

        for (int i = 0; i < sweeps.size(); ++i) {
            wu = sweeps.get(i).applyArm(wu, armIndecies[i]);
            sweeps.get(i).writeNamePair(wName, armIndecies[i]);
        }
        wu.getDocumentElement().setAttribute("name", wName.toString());
        if ( uniqueSeeds ) {
            ((Element)wu.getDocumentElement().getElementsByTagName("parameters").item(0))
            .setAttribute( "iseed", Integer.toString( uniqueSeed ) );
            uniqueSeed += 1;
        }

        return wu;
    }

}
