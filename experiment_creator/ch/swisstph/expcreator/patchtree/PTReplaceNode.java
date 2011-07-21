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

import java.io.Writer;

import javax.xml.transform.Transformer;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Document;
import org.w3c.dom.Node;

/** A leaf node containing a single differing element or text node. */
public class PTReplaceNode extends PTBase {

    private final Node child;

    public PTReplaceNode(Node n) {
        child = n;
    }

    public String getName() {
        return child.getNodeName();
    }

    public int write(Transformer transformer, StreamResult result, String path) throws Exception {
        Writer out = result.getWriter();
        out.write(path + "->" + child.getNodeName());
        out.write('\n');
        transformer.transform(new DOMSource(child), result);
        out.write('\n');
        return 1;
    }

    public int apply(Document document, Node parent, Node node) {
        // In most cases current node is worked out. Here it can't be,
        // because it may one of a list of nodes, but doesn't know which.
        if (node == null) {
            throw new RuntimeException("PTReplaceNode.apply(): I need to know current node!");
        }

        Node imported = document.importNode(child, true);
        parent.replaceChild(imported, node);
        return 1;
    }
}
