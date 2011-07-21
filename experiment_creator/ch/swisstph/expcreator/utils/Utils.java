package ch.swisstph.expcreator.utils;

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

import java.io.StringWriter;

import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerException;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

public class Utils {

	// Helper function to strip old white-space.
	// Source: http://forums.sun.com/thread.jspa?threadID=5201482
	public static void stripWhitespace(Node node, short nodeType, String name) {
		NodeList list = node.getChildNodes();
		for (int i = 0; i < list.getLength(); i++) {
			// Get child node
			Node childNode = list.item(i);
			if (childNode.getNodeType() == nodeType &&
					(name == null ||
							childNode.getNodeName().trim().equals(name) &&
							childNode.getNodeValue().trim().equals(""))) {
				childNode.getParentNode().removeChild(childNode);
				// child was removed so list invalid; easiest is to start again:
				stripWhitespace(node, nodeType, name);
				break;
			}
            stripWhitespace(childNode, nodeType, name);
		}
	}

	public static String toXMLString(Document documentNode) {
		String xmlString = null;
		try
		{
			TransformerFactory tFactory = TransformerFactory.newInstance();
			Transformer transformer = tFactory.newTransformer();
			//transformer.setOutputProperty("omit-xml-declaration", "yes");

			StringWriter sw = new StringWriter();
			StreamResult result = new StreamResult(sw);

			DOMSource source = new DOMSource( documentNode );
			transformer.transform( source, result );

			xmlString = sw.getBuffer().toString();
		}
		catch (TransformerException exception)
		{
			xmlString = null;
		}
		return xmlString;
	}


}
