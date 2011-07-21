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
import java.util.Collections;
import java.util.List;

import javax.xml.transform.Transformer;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Document;
import org.w3c.dom.Node;

/** A leaf node containing a list of differing sub-elements with the same
 * name.
 * 
 * The list may be empty, meaning the patch removes other elements of the
 * same name. There need not exist other elements of the same name, meaning
 * the patch inserts elements. */
public class PTReplaceNodeList extends PTBase {

    private final String name;
    private final String nextElement;
    private final List<Node> childList;

    /** Create a patch to replace one list of nodes with another.
     * 
     * @param name Name of element list
     * @param nextElement Name of expected next element, or null if no next
     * element. Used as a hint for the insert position when there was no old list.
     * @param elements The new elements to insert.
     */
    public PTReplaceNodeList(String name, String nextElement, List<Node> elements) {
        this.name = name;
        this.nextElement = nextElement;
        childList = Collections.unmodifiableList(elements);
    }

    public String getName() {
        return name;
    }

    public int write(Transformer transformer, StreamResult result, String path) throws Exception {
        Writer out = result.getWriter();
        out.write(path + "->" + name + "\n");
        for (Node child : childList) {
            transformer.transform(new DOMSource(child), result);
        }
        out.write('\n');
        return 1;
    }

    public int apply(Document document, Node parent, Node node_unused) {
        List<Node> nodes = getChildNodes(parent, name);
        
        // A marker for where to insert our nodes.
        // We make a guess using nextElement (if null, means at end).
        Node refNode = null;
        if( nodes.size() > 0 ){
            refNode = nodes.get( nodes.size() - 1 ).getNextSibling();
        }else{
            if (nextElement != null) {
                refNode = getChildNodes( parent, nextElement ).get(0);
            }
        }
        
        for (Node child : childList) {
            Node imported = document.importNode(child, true);
            parent.insertBefore(imported, refNode);
        }
        for( Node old : nodes ){
            parent.removeChild( old );
        }
        return childList.size();
    }
}