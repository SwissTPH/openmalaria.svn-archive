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
import java.util.List;
import java.util.TreeMap;

import javax.xml.transform.Transformer;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import ch.swisstph.expcreator.exceptions.PatchConflictException;

/**
 * A base node of the Patch Tree.
 * 
 * Also used to represent patch coverage, where the contents of the patch may be
 * empty but the structure is there.
 */
public abstract class PTBase {

    abstract String getName();

    /**
     * Returns the union of lhs and rhs.
     * 
     * Replacement Elements/Attrs/ are null (used to represent coverage, not to
     * create an applyable patch). Function shouldn't modify lhs or rhs. Either
     * may be passed in as null.
     **/
    public static PTBase union(PTBase lhs, PTBase rhs) {
        if (lhs == null) {
            return rhs;
        } else if (rhs == null) {
            return lhs;
        }
        if (!lhs.getName().equals(rhs.getName())) {
            throw new RuntimeException("Element name mismatch");
        }

        if (lhs instanceof PTReplaceAttr) {
            if (!(rhs instanceof PTReplaceAttr)) {
                // rhs is an element or element list somehow??
                throw new RuntimeException("Attr mismatch");
            }
            return lhs; // both are Attrs (return either)
        } else if (lhs instanceof PTReplaceNode) {
            if (!(rhs instanceof PTReplaceNode || rhs instanceof PTElement)) {
                throw new RuntimeException("Element mismatch");
            }
            return lhs; // both are Elements (return either) or rhs is subset of
                        // lhs
        } else if (lhs instanceof PTElement) {
            if (rhs instanceof PTReplaceNode) {
                return rhs; // lhs subset of rhs
            } else if (!(rhs instanceof PTElement)) {
                throw new RuntimeException("Element mismatch");
            }

            // recurse to child nodes
            TreeMap<String, PTBase> children = new TreeMap<String, PTBase>();
            for (PTBase child : ((PTElement) lhs).getChildren()) {
                children.put(child.getName(), child);
            }
            for (PTBase child : ((PTElement) rhs).getChildren()) {
                String name = child.getName();
                PTBase cur = children.get(name);
                // Replace with union. cur may be null, in which case union
                // equals child.
                children.put(name, union(cur, child));
            }
            return new PTElement(lhs.getName(), new ArrayList<PTBase>(
                    children.values()));
        } else if (lhs instanceof PTReplaceNodeList) {
            if (!(rhs instanceof PTReplaceNodeList || rhs instanceof PTNodeList)) {
                throw new RuntimeException("Element list mismatch");
            }
            return lhs; // as with PTReplaceNode
        } else if (lhs instanceof PTNodeList) {
            if (rhs instanceof PTReplaceNodeList) {
                return rhs; // lhs ⊂ rhs
            } else if (!(rhs instanceof PTNodeList)) {
                throw new RuntimeException("Element list mismatch");
            }
            List<PTBase> lnodes = ((PTNodeList) lhs).getNodes();
            List<PTBase> rnodes = ((PTNodeList) rhs).getNodes();
            // Both lists must match
            int l = lnodes.size();
            assert rnodes.size() == l;
            PTBase[] u = new PTBase[l];

            for (int i = 0; i < l; ++i) {
                u[i] = union(lnodes.get(i), rnodes.get(i));
            }
            return new PTNodeList(lhs.getName(), u);
        } else {
            throw new RuntimeException("unexpected element type: " + lhs);
        }
    }

    /**
     * Checks for overlap between lhs and rhs (non-zero intersection).
     * 
     * Throws if some overlap exists, returns if not.
     */
    public static void checkConflicts(PTBase lhs, PTBase rhs) {
        if (lhs == null || rhs == null) {
            return;
        } // one or both empty
        if (!lhs.getName().equals(rhs.getName())) {
            throw new RuntimeException("Element name mismatch");
        }

        try {
            if (lhs instanceof PTReplaceAttr) {
                if (!(rhs instanceof PTReplaceAttr)) {
                    // rhs is an element or element list somehow??
                    throw new RuntimeException("Attr mismatch");
                }
                throw new PatchConflictException("(Attr)");
            } else if (lhs instanceof PTReplaceNode) {
                if (!(rhs instanceof PTReplaceNode || rhs instanceof PTElement)) {
                    throw new RuntimeException("Element mismatch");
                }
                throw new PatchConflictException("(Element)");
            } else if (lhs instanceof PTElement) {
                if (rhs instanceof PTReplaceNode) {
                    throw new PatchConflictException("(Element)");
                } else if (!(rhs instanceof PTElement)) {
                    throw new RuntimeException("Element mismatch");
                }

                // recurse to child nodes
                TreeMap<String, PTBase> children = new TreeMap<String, PTBase>();
                for (PTBase child : ((PTElement) lhs).getChildren()) {
                    children.put(child.getName(), child);
                }
                for (PTBase child : ((PTElement) rhs).getChildren()) {
                    String name = child.getName();
                    PTBase cur = children.get(name);
                    if (cur != null) {
                        checkConflicts(cur, child);
                    }
                }
                return;
            } else if (lhs instanceof PTReplaceNodeList) {
                if (!(rhs instanceof PTReplaceNodeList || rhs instanceof PTNodeList)) {
                    throw new RuntimeException("Element list mismatch");
                }
                throw new PatchConflictException(lhs.getName()
                        + " -> (Element list)");
            } else if (lhs instanceof PTNodeList) {
                if (rhs instanceof PTReplaceNodeList) {
                    throw new PatchConflictException(lhs.getName()
                            + " -> (Element list)");
                } else if (!(rhs instanceof PTNodeList)) {
                    throw new RuntimeException("Element list mismatch");
                }
                List<PTBase> lnodes = ((PTNodeList) lhs).getNodes();
                List<PTBase> rnodes = ((PTNodeList) rhs).getNodes();
                // Both lists must match
                int l = lnodes.size();
                assert rnodes.size() == l;

                for (int i = 0; i < l; ++i) {
                    checkConflicts(lnodes.get(i), rnodes.get(i));
                }
                return;
            } else {
                System.out.println("unexpected element type: " + lhs);
                throw new RuntimeException("unexpected element type");
            }
        } catch (PatchConflictException e) {
            if (!(lhs instanceof PTNodeList || lhs instanceof PTReplaceNodeList))
                e.pushPath(lhs.getName() + " -> ");
            throw e;
        }
    }

    /**
     * Returns all direct children of node with name name.
     * 
     * Note: not the same as getElementsByTagName(), which finds all
     * descendants.
     */
    public static List<Node> getChildNodes(Node node, String name) {
        ArrayList<Node> r = new ArrayList<Node>();
        NodeList children = node.getChildNodes();
        int l = children.getLength();
        for (int i = 0; i < l; ++i) {
            if (name.equals(children.item(i).getNodeName()))
                r.add(children.item(i));
        }
        return r;
    }

    /**
     * Write element path followed by XML node to result for each leaf node.
     * Return the number of leaves. (Using Transformer to print XML fragments
     * like this doesn't appear to work.)
     */
    public abstract int write(Transformer transformer, StreamResult result,
            String path) throws Exception;

    /**
     * Apply patch on top of Node parent in Document document.
     * 
     * Parameter node is the current node being visited; it is often not passed
     * (null), but sometimes is required.
     * 
     * Return the number of patches applied. parent must be an Element or a
     * Document.
     */
    public abstract int apply(Document document, Node parent, Node node);
}
