package com.swisstph.expcreator.arms;

import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.Enumeration;
import java.util.Hashtable;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.w3c.dom.Document;
import org.w3c.dom.Element;

import com.swisstph.expcreator.CombineSweeps;
import com.swisstph.expcreator.utils.Utils;

public class ArmTxt extends Arm{

	// The differences represented by this branch. null if no differences.
	private int id = -1;		// arm's DB ID
	private final String name;	// file name
	private final String label;	// label; called 'value' in database; from scenario's 'name' attribute
	private final Element base;
	private final Hashtable<String,String> parameters;

	public ArmTxt(Element base, File txt ) {
		
		super(base,txt);

		String tname = txt.getName();
		assert tname.endsWith(".txt");

		this.base=base;
		this.name = tname.substring(0,tname.length() - 4 );
		this.label = this.name;

		this.parameters = new Hashtable<String, String>();
		FileReader fr = null;
		BufferedReader br = null;

		try {

			// read file
			fr = new FileReader(txt);
			br = new BufferedReader(fr);

			// and match regular expression : @\w+@:\w+ (e.g. @IIR@:0.60)
			Pattern pattern = Pattern.compile("(@\\w+@):([\\S \\t]+)");
			Matcher matcher = null;

			String strLine = null;
			while( (strLine = br.readLine() ) != null ) {

				matcher = pattern.matcher(strLine);

				if(matcher.find()) {
					String param_name = matcher.group(1);
					String param_value = matcher.group(2);
					parameters.put(param_name, param_value);
				} else if ( strLine.equals("\n") || strLine.equals("\r\n") ) {
					// nothing to do empty line
				}
				else {
					System.err.println( "Error in file " + tname + " : '" + strLine + "' doesn't match the expression @[parameter_name]@:[value]");
				}
			}

		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		System.out.print("ArmTxt:\t" + name);

	}

	// generate patch
	public void writePatch(File dir) throws Exception {

	}

	// apply to document
	public Document apply(Document document) throws Exception {
		
		String xmlString = Utils.toXMLString(document);

		Enumeration<String> enParams = parameters.keys();
		while(enParams.hasMoreElements()){

			String param_name = enParams.nextElement();
			String param_value = parameters.get(param_name);

			xmlString= xmlString.replace(param_name, param_value);
		}
		
		return CombineSweeps.getBuilder().parse( new ByteArrayInputStream( xmlString.getBytes()) );
		
	}

}
