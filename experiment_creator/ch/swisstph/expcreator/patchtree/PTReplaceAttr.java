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

import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;

/** A leaf node containing a single differing attribute. */
public class PTReplaceAttr extends PTBase {

    private final Attr child;

    public PTReplaceAttr(Attr n) {
        child = n;
        // System.out.println(
        // "new Attr: "+child.getNodeName()+"="+child.getNodeValue() );
    }

    public String getName() {
        return child.getName();
    }

    public int write(Transformer transformer, StreamResult result, String path)
            throws Exception {
        Writer out = result.getWriter();
        out.write(path + "->" + child.getNodeName());
        out.write('\n');
        transformer.transform(new DOMSource(child), result);
        out.write('\n');
        return 1;
    }

    public int apply(Document document, Node parent, Node node_unused) {
        Element parElt = (Element) parent;
        if (parElt == null) {
            throw new RuntimeException("document shouldn't have attributes");
        }
        Attr old = parElt.getAttributeNode(child.getNodeName());
        if (old == null) // Patching works on the basis of replacing one element
                         // with another.
        {
            throw new RuntimeException("error resolving base attribute "
                    + child.getNodeName());
        }
        old.setValue(child.getValue());
        return 1;
    }
}
