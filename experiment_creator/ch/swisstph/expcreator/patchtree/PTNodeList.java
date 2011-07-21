package ch.swisstph.expcreator.patchtree;

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

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import javax.xml.transform.Transformer;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Document;
import org.w3c.dom.Node;

/** A node representing a list of nodes of the same name
 * (elements or text nodes).
 *
 * This is an intermediate type, since given a list of XML nodes with the
 * same name (elements or text nodes) we need to handle them as one entity.
 */
public class PTNodeList extends PTBase {
    private final String name;
    private final List<PTBase> nodes;   // nodes may be null: not all in list may need patching

    public PTNodeList(String n, PTBase[] c) {
        name = n;
        nodes = Collections.unmodifiableList(Arrays.asList(c));
    }
    // Convenience constructor for a single child node
    public PTNodeList(String n, PTBase c) {
        name = n;
        ArrayList<PTBase> nList = new ArrayList<PTBase>();
        nList.add(c);
        nodes = Collections.unmodifiableList(nList);
    }

    public String getName() {
        return name;
    }

    public int write(Transformer transformer, StreamResult result, String path) throws Exception {
        int n = 0;
        for (PTBase node : nodes) {
            if( node != null )
                n += node.write(transformer, result, path);
        }
        return n;
    }

    public int apply(Document document, Node parent, Node node_unused) {
        List<Node> nodes = getChildNodes(parent, name);
        if (nodes.size() != this.nodes.size()) {
            // must have been incorrectly reckoned somewhere
            throw new RuntimeException("Node list length mismatch");
        }
        int n = 0;
        for (int i = 0; i < this.nodes.size(); ++i) {
            if( this.nodes.get(i) != null )
                n += this.nodes.get(i).apply(document, parent, nodes.get(i));
        }
        return n;
    }
    
    public List<PTBase> getNodes(){
    	return this.nodes;
    }
}