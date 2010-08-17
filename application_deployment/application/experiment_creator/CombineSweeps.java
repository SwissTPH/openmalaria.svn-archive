// This file is part of OpenMalaria.
// Copyright (C) 2005-2010 Swiss Tropical Institute and Liverpool School Of Tropical Medicine

import java.util.ArrayList;
import java.io.*;
import javax.xml.parsers.*;
import javax.xml.transform.*;
import javax.xml.transform.dom.*;
import javax.xml.transform.stream.StreamResult;
import org.w3c.dom.*;

/** A tool to exponentially combine sweeps.
 *
 * An experiment should be composed of a base scenario and a set
 * of sweeps. Each sweep should be composed of a set of arms. Each
 * arm should be a scenario differing from the base in some way.
 * 
 * Arms are converted to a diff against the base, which can then be
 * patched against other scenarios.
 * 
 * An experiment can then factorially combined by taking all possible
 * combinations of one arm from each sweep, and in each case patching
 * the arms' diffs into the base scenario.
 * 
 * For ease of use, each sweep has one arm, the "no change" arm,
 * added automatically, and one sweep is added: the random seeds
 * sweep.
 *********************************************************************/
public class CombineSweeps {
    class DiffException extends RuntimeException {
	public static final long serialVersionUID = 1L;	// avoid a warning (we don't need serialization...)
	DiffException( String msg ){
	    super( msg );
	}
    }
    class PatchException extends RuntimeException {
	public static final long serialVersionUID = 1L;	// avoid a warning (we don't need serialization...)
	PatchException( String msg ){
	    super( msg );
	}
    }
    
    class XMLFileFilter implements FilenameFilter {
	public boolean accept( File dir, String name ){
	    return name.endsWith( ".xml" );
	}
    }
    class BaseXMLFileFilter implements FilenameFilter {
	public boolean accept( File dir, String name ){
	    return name.equals( "base.xml" );
	}
    }
    
    /** An Arm represents a patch against the base document, and is
     * one option of a sweep. */
    class Arm{
	// A generic node of the patch tree
	private abstract class PatchNode {
	    // Write element path followed by XML node to result for each
	    // leaf node, returning number of leaves.
	    abstract int write( StreamResult result, String path ) throws Exception;
	    
	    // Apply patch on top of parent Node in Document document;
	    // return number of patches.
	    // parent must be an Element or a Document.
	    abstract int apply( Document document, Node parent );
	}
	// A node containing children of the patch; its presence implies
	// that at least one descendant node differs.
	private class PatchChildNode extends PatchNode {
	    private String name;
	    private ArrayList<PatchNode> children;
	    
	    PatchChildNode( String n, ArrayList<PatchNode> c ){
		name = n;
		children = c;
	    }
	    // Convenience constructor for a single child node
	    PatchChildNode( String n, PatchNode c ){
		name = n;
		children = new ArrayList<PatchNode>();
		children.add( c );
	    }
	    
	    int write( StreamResult result, String path ) throws Exception{
		path += "->" + name;
		int n = 0;
		for( PatchNode child : children )
		    n += child.write( result, path );
		return n;
	    }
	    
	    int apply( Document document, Node parent ){
		Element node;
		if( parent instanceof Document ){	// root element
		    Document parDoc = (Document)parent;
		    node = (Element) parDoc.getElementsByTagName( name ).item( 0 );
		} else {
		    Element parElt = (Element)parent;
		    node = (Element) parElt.getElementsByTagName( name ).item( 0 );
		}
		if( node == null )
		    throw new PatchException( "error resolving element "+name );
		int n = 0;
		for( PatchNode child : children )
		    n += child.apply( document, node );
		return n;
	    }
	}
	// A leaf node containing a single differing element
	private class PatchElement extends PatchNode {
	    private Element child;
	    
	    PatchElement( Element n ){
		child = n;
		assert( child != null );
	    }
	    
	    int write( StreamResult result, String path ) throws Exception{
		Writer out = result.getWriter();
		out.write( path + "->" + child.getNodeName() );
		out.write( '\n' );
		transformer.transform( new DOMSource( child ), result );
		out.write( '\n' );
		return 1;
	    }
	    
	    int apply( Document document, Node parent ){
		String name = child.getNodeName();
		Node node;
		if( parent instanceof Document ){	// root element
		    Document parDoc = (Document)parent;
		    node = parDoc.getElementsByTagName( name ).item( 0 );
		} else {
		    Element parElt = (Element)parent;
		    node = parElt.getElementsByTagName( name ).item( 0 );
		}
		if( node == null )
		    // Patching works on the basis of replacing one element with another.
		    throw new PatchException( "error resolving element "+name );
		
		Node imported = document.importNode( child, true );
		parent.replaceChild( imported, node );
		return 1;
	    }
	}
	// A leaf node containing a single differing attribute
	private class PatchAttr extends PatchNode {
	    private Attr child;
	    
	    PatchAttr( Attr n ){
		child = n;
		assert( child != null );
// 		System.out.println( "new Attr: "+child.getNodeName()+"="+child.getNodeValue() );
	    }
	    
	    int write( StreamResult result, String path ) throws Exception{
		Writer out = result.getWriter();
		out.write( path + "->" + child.getNodeName() );
		out.write( '\n' );
		transformer.transform( new DOMSource( child ), result );
		out.write( '\n' );
		return 1;
	    }
	    
	    int apply( Document document, Node parent ){
		Element parElt = (Element) parent;
		if( parElt == null )
		    throw new PatchException( "document shouldn't have attributes" );
		Attr old = parElt.getAttributeNode( child.getNodeName() );
		if( old == null )
		    // Patching works on the basis of replacing one element with another.
		    throw new PatchException( "error resolving base attribute "+child.getNodeName() );
		old.setValue( child.getValue() );
		return 1;
	    }
	}
	
	// The differences represented by this branch. null if no differences.
	private String name;
	private PatchNode patch;
	
	/** Constructor; generates a patch from passed document and base. */
	public Arm( File xml ) throws Exception{
	    Document document = builder.parse( xml );
	    Element elt = document.getDocumentElement();
	    
	    name = xml.getName();
	    patch = diffRecurse( elt, baseElement );
	}
	/** Constructor for a no-effect arm. */
	public Arm() {
	    name = "no_change";
	    patch = null;
	}
	/** Constructor setting random seed to n. */
	public Arm( int n ){
	    name = Integer.toString( n );
	    Document document = builder.newDocument();
	    Attr seed = document.createAttribute( "iseed" );
	    seed.setValue( name );
	    
	    patch = new PatchChildNode( "scenario",
		new PatchChildNode( "model",
		    new PatchChildNode( "parameters",
			new PatchAttr( seed )
	    ) ) );
	}
	
	public boolean isNull() {
	    return patch == null;
	}
	
	public void writePatch( File dir ) throws Exception {
	    FileWriter fileW = new FileWriter( new File( dir, name ) );
	    BufferedWriter out = new BufferedWriter( fileW  );
	    StreamResult result = new StreamResult( out );
	    
	    int nChildren = 0;
	    if( patch != null )
		nChildren = patch.write( result, "" );
	    
	    out.close();
	    
	    System.out.println( "Written: "+name+" ("+nChildren+" leaf patches)" );
	}
	
	public void apply( Document document ) throws Exception {
// 	    System.out.print( "Applying "+(patch==null?"void":"")+" arm "+name+": " );
	    int n = 0;
	    if( patch != null ){
		n = patch.apply( document, document );
	    }
// 	    System.out.println( n+" nodes patched" );
	}
	
	// Finds differences of arm node against base node and saves these into a
	// representation of all changed elements of this Arm.
	private PatchNode diffRecurse( Node armNode, Node baseNode ) throws Exception{
	    assert( armNode != null );
	    assert( baseNode != null );
	    
	    short nodeType = armNode.getNodeType();
	    if( nodeType != baseNode.getNodeType() )
		throw new DiffException( "elements have different type!" );
	    switch( nodeType ){
		case Node.COMMENT_NODE:
		    return null;	// don't care much for comments
		case Node.ATTRIBUTE_NODE:
		    if( !armNode.getNodeName().equals( baseNode.getNodeName() )
			|| !armNode.getNodeValue().equals( baseNode.getNodeValue() ) )
			return new PatchAttr( (Attr)armNode );
		    else
			return null;	// identical
		case Node.ELEMENT_NODE:
		    break;		// handle below
		case Node.TEXT_NODE:
		    if( !armNode.getNodeName().equals( baseNode.getNodeName() )
			|| !armNode.getTextContent().equals( baseNode.getTextContent() ) )
			// Elements are different
			return new PatchElement( (Element)armNode );
		    else
			return null;
		default:
		    throw new DiffException( "unexpected element type: "+nodeType+" (named "+armNode.getNodeName()+")" );
	    }
	    
	    if(
		!armNode.getNodeName().equals( baseNode.getNodeName() )
		|| armNode.getAttributes().getLength() != baseNode.getAttributes().getLength()
	    ){
		// Elements are different
		return new PatchElement( (Element)armNode );
	    }
	    
	    ArrayList<PatchNode> differentNodes = new ArrayList<PatchNode>();
	    
	    int len = armNode.getAttributes().getLength();
	    for( int i = 0; i < len; ++i ){
		PatchNode r = diffRecurse( armNode.getAttributes().item(i), baseNode.getAttributes().item(i) );
		if( r != null )
		    differentNodes.add( r );
	    }
	    
	    // check sub-nodes (largely elements/attributes)
	    NodeList subE = armNode.getChildNodes();
	    NodeList subB = baseNode.getChildNodes();
// 	    System.out.println( subE.getLength()+"; "+subB.getLength() );
	    
	    //Note:
	    // if order and elements are the same, OK
	    // if order is different: in some cases OK, in others not...
	    
	    if( subE.getLength() != subB.getLength() ){
		// Missing/extra elements
		return new PatchElement( (Element)armNode );
	    }
	    
	    len = subE.getLength();
	    for( int i = 0; i < len; ++i ){
		PatchNode r = diffRecurse( subE.item(i), subB.item(i) );
		if( r != null )
		    differentNodes.add( r );
	    }
	    
	    if( differentNodes.size() != 0 ){
		// We have some differences
		//TODO: should ignore differences in order in _some_ cases
		return new PatchChildNode( armNode.getNodeName(), differentNodes );
	    }
	    
	    // Nodes and their decendants are identical
	    return null;
	}
    }
    
    /** A Sweep represents one set of changes (Arms), one of which must
     * be chosen for each scenario. */
    class Sweep{
	private String name;
	private ArrayList<Arm> arms;
	
	// Construct sweep with name fName and arms read from armXmls
	public Sweep( String fName, File[] armXmls ) throws Exception{
	    name = fName;
	    
	    arms=new ArrayList<Arm>();
	    arms.ensureCapacity( armXmls.length );
	    
	    for( File armXml : armXmls ){
		arms.add( new Arm( armXml ) );
	    }
	}
	
	// Construct sweep with name fName and arms from nSeeds different seeds
	public Sweep( String fName, int nSeeds ) throws Exception{
	    name = fName;
	    
	    arms=new ArrayList<Arm>();
	    arms.ensureCapacity( nSeeds );
	    
	    for( int i = 1; i <= nSeeds; ++i ){	// first seed should be 1
		arms.add( new Arm( i ) );
	    }
	}
	
	int getLength(){
	    return arms.size();
	}
	
	/** If no no-change arm already exists, this adds one (otherwise,
	 * does nothing). */
	public void addDefaultArm() {
	    for( Arm arm : arms ){
		if( arm.isNull() )
		    return;	// have a no-effect arm
	    }
	    arms.add( new Arm() );
	}
	
	void writePatches( File parentOutDir ) throws Exception{
	    File outDir = new File( parentOutDir, name );
	    outDir.mkdir();
	    
	    for( Arm arm : arms )
		arm.writePatch( outDir );
	}
	
	void applyArm( Document document, int index ) throws Exception{
	    arms.get( index ).apply( document );
	}
    }
    
    private FilenameFilter xmlFilter;
    private Transformer transformer;
    
    private DocumentBuilder builder;
    private Document baseDocument;
    private Element baseElement;
    
    private ArrayList<Sweep> sweeps;
    
    // Generate a Sweep from a directory iff it contains XML files.
    private void readSweep( File dir ) throws Exception{
	if( !dir.isDirectory() )
	    return;
	
	File[] xmlFiles = dir.listFiles( xmlFilter );
	if( xmlFiles.length == 0 )
	    return;
	
	Sweep sweep = new Sweep( dir.getName(), xmlFiles );
	sweeps.add( sweep );
    }
    
    void readSweeps( String inputPath ) throws Exception {
	xmlFilter = new XMLFileFilter();
	builder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
	sweeps = new ArrayList<Sweep>();
	
	File inputDir = new File( inputPath );
	if( !inputDir.isDirectory() ){
	    System.err.println( "INPUT_DIR is not a directory: "+inputPath );
	    System.exit( 1 );
	}
	
	// Read base XML file
	File[] baseXMLs = inputDir.listFiles( new BaseXMLFileFilter() );
	if( baseXMLs.length != 1 ){
	    System.err.println( "Expected base.xml file in INPUT_DIR." );
	    System.exit( 1 );
	}
	baseDocument = builder.parse( baseXMLs[0] );
	baseElement = baseDocument.getDocumentElement();
	
	for( File subdir : inputDir.listFiles() )
	    readSweep( subdir );
    }
    
    void writePatches( String outputPath ) throws Exception {
	transformer = TransformerFactory.newInstance().newTransformer();
	transformer.setOutputProperty( OutputKeys.ENCODING, "UTF-8" );
	transformer.setOutputProperty( OutputKeys.METHOD, "xml" );
	transformer.setOutputProperty( OutputKeys.OMIT_XML_DECLARATION, "yes" );
	
	File outputDir = new File( outputPath );
	if( !outputDir.isDirectory() || outputDir.list().length != 0 || !outputDir.canWrite() ){
	    System.err.println( "OUTPUT_DIR is not a writable empty directory: "+outputPath );
	    System.exit( 1 );
	}
	
	for( Sweep sweep : sweeps )
	    sweep.writePatches( outputDir );
    }
    
    void combine( String outputPath ) throws Exception {
	transformer = TransformerFactory.newInstance().newTransformer();
	transformer.setOutputProperty( OutputKeys.ENCODING, "UTF-8" );
	transformer.setOutputProperty( OutputKeys.METHOD, "xml" );
	
	File outputDir = new File( outputPath );
	if( !outputDir.isDirectory() || outputDir.list().length != 0 || !outputDir.canWrite() ){
	    System.err.println( "OUTPUT_DIR is not a writable empty directory: "+outputPath );
	    System.exit( 1 );
	}
	
	int combinations = 1;
	int[] lengths = new int[ sweeps.size() ];
	for( int i = 0; i < lengths.length; ++i ){
	    lengths[i] = sweeps.get( i ).getLength();
	    combinations *= lengths[i];
	}
	
	for( int c = 0; c < combinations; ++c ){
	    // Clone our base
	    DOMResult cloneResult = new DOMResult();
	    transformer.transform( new DOMSource( baseDocument ), cloneResult );
	    Document wu = (Document)cloneResult.getNode();
	    
	    int div = 1;
	    for( int i = 0; i < sweeps.size(); ++i ){
		int index = (c / div) % lengths[i];
		div *= lengths[i];
		
		sweeps.get( i ).applyArm( wu, index );
	    }
	    
	    // Write out result:
	    String name = "wuE_"+Integer.toString( c )+".xml";
	    FileWriter fileW = new FileWriter( new File( outputDir, name ) );
	    BufferedWriter out = new BufferedWriter( fileW  );
	    StreamResult result = new StreamResult( out );
	    transformer.transform( new DOMSource( wu ), result );
	    out.close();
	}
    }
    
    void addSeedsSweep( int nSeeds ) throws Exception{
	Sweep sweep = new Sweep( "seeds", nSeeds );
	sweeps.add( sweep );
    }
    
    public static void main(String[] args) {
	String inputDir = null, outputDir = null;
	int nSeeds = -1;
	boolean defaultArms = false;
	boolean patches = false;
	
	for (int i = 0; i < args.length; i++) {
	    if (args[i].startsWith("--")) {
		if (args[i].equals("--seeds"))
		    nSeeds = Integer.parseInt(args[++i]);
		else if (args[i].equals("--default-arms"))
		    defaultArms = true;
		else if (args[i].equals("--patches"))
		    patches = true;
		else
		    printHelp();
	    } else {
		if( inputDir == null )
		    inputDir = args[i];
		else if( outputDir == null )
		    outputDir = args[i];
		else
		    printHelp();
	    }
	}
	
	if( inputDir == null || outputDir == null ){
	    System.err.println("Required arguments: INPUT_DIR OUTPUT_DIR");
	    printHelp();
	}
	
	CombineSweeps mainObj = new CombineSweeps();
	
	try{
	    // Find all sweeps
	    mainObj.readSweeps( inputDir );
	    
	    if( defaultArms ){
		for( Sweep sweep : mainObj.sweeps )
		    sweep.addDefaultArm();
	    }
	    
	    if( nSeeds >= 0 )
		mainObj.addSeedsSweep( nSeeds );
	    
	    // TODO: make sure sweeps don't clash
	    
	    if( patches )
		mainObj.writePatches( outputDir );
	    else{
		mainObj.combine( outputDir );
		// TODO: factorially combine all sweeps into a set of scenarios, validate and write out
		// TODO: work out how to name resulting scenarios and make sweeps/arms known to analyser
	    }
	}catch(Exception e){
	    e.printStackTrace();
	    System.exit( 1 );
	}
	// Done.
    }
    
    public static void printHelp() {
	System.out.println("Usage: CombineSweeps [options] INPUT_DIR OUTPUT_DIR\n"
	    +"\nOptions:\n"
	    +"  --seeds N		Add a sweep of N random seeds\n"
	    +"  --default-arms	Add one arm to each sweep, with no change against\n"
	    +"			base scenario (for sweeps not already having one).\n"
	    +"  --patches		Write out arms as patches instead of resulting\n"
	    +"			combined XML files. (Currently broken.)\n"
	    +"\nINPUT_DIR should contain one XML file named base.xml and a set of\n"
	    +"sub-directories. Each sub-directory containing any XML files is\n"
	    +"considered a sweep. Each XML file within each sweep's directory is\n"
	    +"considered an arm. Extra arms/sweeps are added according to options.\n"
	    +"Sweeps are then combined factorially (all combinations of one arm\n"
	    +"from each sweep)."
	);
	System.exit( 1 );
    }
}
