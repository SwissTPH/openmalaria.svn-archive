package com.swisstph.expcreator.arms;

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

import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;

import com.swisstph.expcreator.CombineSweeps;



/** An Arm represents a patch against the base document, and is
 * one option of a sweep. */
public abstract class Arm {
    // The differences represented by this branch. null if no differences.
    protected int id = -1;		// arm's DB ID
    protected final String name;	// file name
    protected final String label;	// label; called 'value' in database; from scenario's 'name' attribute
    protected final Element base;

    /** Constructor; generates a patch from passed document and base. */
    public Arm(Element base, File file) {
    	
		String tname = file.getName();
		this.base=base;
		this.name = tname.substring(0,tname.length() - 4 );
		this.label = this.name;
    }

    /** Constructor setting random seed to n. */
    public Arm(int n) {
        name = Integer.toString(n);
        label = name;
        Document document = CombineSweeps.getBuilder().newDocument();
        Attr seed = document.createAttribute("iseed");
        seed.setValue(name);
        
        base = null;
    }

    public int getId() {
        if (id < 0) {
            throw new RuntimeException("Arm: not got ID yet");
        }
        return id;
    }

    public String getName() {
        return name;
    }

    public void updateDb(Connection conn, int sweepId, boolean isComparator) throws Exception {
        // arms TABLE: arm_id(auto key), exp_id, swe_id, value, name, comparator
        // Details arm names, associated sweep and comparator.
        // Value is "label" of plots; taken from scenario's name attribute; name is file-name
        String sql = "INSERT INTO arms (exp_id,swe_id,value,name,comparator) VALUES (?,?,?,?,?)";
        PreparedStatement pstmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS);
        pstmt.setInt(1, CombineSweeps.getExpId());
        pstmt.setInt(2, sweepId);
        pstmt.setString(3, label);
        pstmt.setString(4, name);
        pstmt.setString(5, isComparator ? "T" : "F");
        pstmt.executeUpdate();
        ResultSet rs = pstmt.getGeneratedKeys();
        if (rs.next()) {
            id = rs.getInt(1);	// get generated ID
        } else {
            System.out.println("DB error: unable to get generated key");
            throw new RuntimeException("unable to get generated key");
        }
    }

    public abstract void writePatch(File dir) throws Exception;
    public abstract Document apply(Document document) throws Exception;
    
}
