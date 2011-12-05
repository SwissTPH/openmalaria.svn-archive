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
import java.util.Collections;
import java.util.List;

import javax.xml.transform.Transformer;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Document;
import org.w3c.dom.Node;

/**
 * A patch against a single element.
 * 
 * A list of sub-elements of the same name is represented as a single child
 * node.
 */
public class PTElement extends PTBase {
    // Name of element
    private final String name;
    // Patches against lists of sub-elements and attributes
    private final List<PTBase> children;

    public PTElement(String n, List<PTBase> c) {
        name = n;
        children = Collections.unmodifiableList(c);
    }

    // Convenience constructor for a single child node
    public PTElement(String n, PTBase c) {
        name = n;
        ArrayList<PTBase> cList = new ArrayList<PTBase>();
        cList.add(c);
        children = Collections.unmodifiableList(cList);
    }

    public String getName() {
        return name;
    }

    public int write(Transformer transformer, StreamResult result, String path)
            throws Exception {
        path += "->" + name;
        int n = 0;
        for (PTBase child : children) {
            n += child.write(transformer, result, path);
        }
        return n;
    }

    public int apply(Document document, Node parent, Node node) {
        // In most cases current node is worked out. Here it can't be,
        // because it may be one of a list of nodes, and doesn't know which.
        if (node == null) {
            throw new RuntimeException(
                    "PTElement.apply(): I need to know current node!");
        }

        int n = 0;
        for (PTBase child : children) {
            n += child.apply(document, node, null);
        }
        return n;
    }

    public List<PTBase> getChildren() {
        return this.children;
    }
}
