package ch.swisstph.expcreator.arms;

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

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.TreeMap;
import java.util.Map.Entry;

import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Attr;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import ch.swisstph.expcreator.CombineSweeps;
import ch.swisstph.expcreator.patchtree.PTBase;
import ch.swisstph.expcreator.patchtree.PTElement;
import ch.swisstph.expcreator.patchtree.PTNodeList;
import ch.swisstph.expcreator.patchtree.PTReplaceAttr;
import ch.swisstph.expcreator.patchtree.PTReplaceNode;
import ch.swisstph.expcreator.patchtree.PTReplaceNodeList;
import ch.swisstph.expcreator.utils.Utils;

/**
 * An Arm represents a patch against the base document, and is one option of a
 * sweep.
 */
public class ArmXml extends Arm {

    private final PTBase patch; // root node of patch tree

    /** Constructor; generates a patch from passed document and base. */
    public ArmXml(Element base, File xml) throws Exception {

        super(base, xml);
        assert xml.getName().endsWith(".xml"); // should already have been
                                               // checked

        Document document = CombineSweeps.getBuilder().parse(xml);
        Element elt = document.getDocumentElement();
        elt.setAttribute("name", ""); // make sure this Attr isn't patched

        // Reformat: remove all whitespace nodes
        Utils.stripWhitespace(elt, org.w3c.dom.Node.TEXT_NODE, "#text");
        document.normalize();

        try {
            if (CombineSweeps.getValidator() != null) {
                CombineSweeps.getValidator().validate(new DOMSource(document));
            }
        } catch (SAXException e) {
            System.out.println("Validation failure reading" + xml.getName()
                    + ":");
            System.out.println(e.getMessage());
            throw new RuntimeException("validation failure");
        }

        if (!base.getNodeName().equals(elt.getNodeName())) {
            System.out.println("root element name differs: "
                    + base.getNodeName() + ", " + elt.getNodeName());
            throw new RuntimeException("root element name mismatch");
        }

        System.out.print("ArmXml:\t" + name);

        patch = diffRecurse(elt, base);
    }

    /** Constructor setting random seed to n. */
    public ArmXml(int n) {

        super(n);
        Document document = CombineSweeps.getBuilder().newDocument();
        Attr seed = document.createAttribute("iseed");
        seed.setValue(name);

        patch = new PTElement("scenario", new PTNodeList("model",
                new PTElement("model", new PTNodeList("parameters",
                        new PTElement("parameters", new PTReplaceAttr(seed))))));
    }

    public PTBase getPatchCoverage() {
        return patch; // in theory, we could return an immutible version
    }

    public void writePatch(File dir) throws Exception {
        FileWriter fileW = new FileWriter(new File(dir, name));
        BufferedWriter out = new BufferedWriter(fileW);
        StreamResult result = new StreamResult(out);

        int nChildren = 0;
        if (patch != null) {
            nChildren = patch.write(CombineSweeps.getTransformer(), result, "");
        }

        out.close();

        System.out.println("Written: " + name + " (" + nChildren
                + " leaf patches)");
    }

    public Document apply(Document document) throws Exception {

        try {
            /* int n = 0; // count number of patches applied */
            if (patch != null) {
                /* n = */patch.apply(document, null,
                        document.getDocumentElement());
            }
        } catch (Exception e) {
            throw e;
        }

        return document;
    }

    // Finds differences of arm node against base node and saves these into a
    // representation of all changed elements of this Arm.
    // Assumes the nodes already have the same name, since otherwise the
    // parent element is considered to differ.
    private PTBase diffRecurse(Node armNode, Node baseNode) throws Exception {
        assert (armNode != null);
        assert (baseNode != null);
        assert (armNode.getNodeName().equals(baseNode.getNodeName()));

        short nodeType = armNode.getNodeType();
        if (nodeType != baseNode.getNodeType()) {
            System.out.println("elements " + armNode.getNodeName()
                    + " have different type!");
            throw new RuntimeException("elements type mismatch");
        }
        switch (nodeType) {
        case Node.ELEMENT_NODE:
            break; // handle below
        case Node.COMMENT_NODE:
        case Node.TEXT_NODE:
            if (!armNode.getTextContent().equals(baseNode.getTextContent())) {
                assert armNode.getNodeName().equals("#text")
                        || armNode.getNodeName().equals("#comment");
                // Text content is different; is treated as a Node in the DOM
                // tree
                return new PTReplaceNode(armNode);
            }
            return null;
        default:
            System.out.println("unexpected element type: " + nodeType
                    + " (named " + armNode.getNodeName() + ")");
            throw new RuntimeException("unexpected element");
        }

        if (armNode.getAttributes().getLength() != baseNode.getAttributes()
                .getLength()) {
            // different number of attributes: element differs
            return new PTReplaceNode(armNode);
        }

        ArrayList<PTBase> differentNodes = new ArrayList<PTBase>();

        int len = armNode.getAttributes().getLength();
        for (int i = 0; i < len; ++i) {
            Node armAttr = armNode.getAttributes().item(i);
            Node baseAttr = baseNode.getAttributes().item(i);

            if (!armAttr.getNodeName().equals(baseAttr.getNodeName())) // different
                                                                       // attributes:
                                                                       // this
                                                                       // element
                                                                       // differs
            {
                return new PTReplaceNode(armNode);
            }

            if (!armAttr.getNodeValue().equals(baseAttr.getNodeValue())) {
                differentNodes.add(new PTReplaceAttr((Attr) armAttr));
            }
        }
        // If non-empty, contents are aggregated along with differing
        // sub-elements.

        // We aggregate lists of elements. That way, one list can be
        // swapped for another, and we can allow order to change.

        /* Lists all elements in arm and in base with same name. */
        class ArmBasePair {

            ArrayList<Node> arm, base;

            ArmBasePair() {
                arm = new ArrayList<Node>();
                base = new ArrayList<Node>();
            }
        }
        TreeMap<String, ArmBasePair> eltLists = new TreeMap<String, ArmBasePair>();

        NodeList subE = armNode.getChildNodes();
        len = subE.getLength();
        for (int i = 0; i < len; ++i) {
            // get (or create) list
            String name = subE.item(i).getNodeName();
            ArmBasePair list = eltLists.get(name);
            if (list == null) {
                list = new ArmBasePair();
                eltLists.put(name, list);
            }
            // append into eltLists
            list.arm.add(subE.item(i));
        }
        subE = baseNode.getChildNodes();
        len = subE.getLength();
        for (int i = 0; i < len; ++i) {
            // get (or create) list
            String name = subE.item(i).getNodeName();
            ArmBasePair list = eltLists.get(name);
            if (list == null) {
                list = new ArmBasePair();
                eltLists.put(name, list);
            }
            // append into eltLists
            list.base.add(subE.item(i));
        }

        /*
         * We now have a list of all sub-element lists. For each sub-element
         * list:
         */
        Iterator<Entry<String, ArmBasePair>> it = eltLists.entrySet()
                .iterator();
        while (it.hasNext()) {
            Entry<String, ArmBasePair> entry = it.next();
            ArmBasePair ab = entry.getValue();
            // check for equality
            if (ab.arm.size() == ab.base.size()) {
                // equal dim.; are all elements equal?
                boolean allEqual = true;
                PTBase[] patchList = new PTBase[ab.arm.size()];
                for (int i = 0; i < ab.arm.size(); ++i) {
                    patchList[i] = diffRecurse(ab.arm.get(i), ab.base.get(i));
                    if (patchList[i] != null) {
                        allEqual = false;
                    }
                }
                if (allEqual) // all elements equal so nothing to patch
                {
                    continue;
                }
                // equal dimensions; we patch each element in turn
                differentNodes.add(new PTNodeList(entry.getKey(), patchList));
            } else {
                // not equal dimensions; replace the whole list
                assert !(ab.arm.isEmpty() && ab.base.isEmpty());

                // If no base elements, patch won't know where to insert
                // new elements. Help out by telling it where element are
                // in arm.
                String nextElement = null; // null means insert at end
                if (!ab.arm.isEmpty()) {
                    Node last = ab.arm.get(ab.arm.size() - 1);
                    Node next = last.getNextSibling(); // null if at end
                    if (next != null) {
                        nextElement = next.getNodeName();
                    }
                }
                differentNodes.add(new PTReplaceNodeList(entry.getKey(),
                        nextElement, ab.arm));
            }
        }

        if (differentNodes.size() != 0) {
            // We have some differences
            return new PTElement(armNode.getNodeName(), differentNodes);
        }

        // Nodes and their decendants are identical
        return null;
    }
}
