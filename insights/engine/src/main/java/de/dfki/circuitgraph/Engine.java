package de.dfki.circuitgraph;

// System Imports
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.FileNotFoundException;

import java.nio.file.Files;
import java.nio.file.Paths;

// Third-Party Imports
import org.apache.jena.riot.RDFDataMgr;
import org.apache.jena.riot.Lang;

import org.apache.jena.rdf.model.Model;
import org.apache.jena.rdf.model.ModelFactory;
import org.apache.jena.rdf.model.Statement;

import org.apache.jena.rdf.model.InfModel;
import org.apache.jena.reasoner.rulesys.GenericRuleReasoner;
import org.apache.jena.reasoner.rulesys.Rule;

// CLI Parsing Imports
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.apache.commons.cli.GnuParser;

public class Engine {

  public static void main(String[] args) throws java.io.IOException, FileNotFoundException, ParseException {

    String rulesPreprocess = Engine.getPreprocessRules();
    String rules = Engine.loadRules();

    CommandLine cmd = Engine.parseCLI(args);
    String fileIn = cmd.getOptionValue("input");
    String fileOut = cmd.getOptionValue("output");
  
    // Load Model
    Model rawModel = ModelFactory.createDefaultModel();
    rawModel.read(new FileReader(new File(fileIn)), null, "TTL");
      
    // Preprocess Model
    GenericRuleReasoner preprocessReasoner = new GenericRuleReasoner(Rule.parseRules(rulesPreprocess));
    InfModel preprocessedModel = ModelFactory.createInfModel(preprocessReasoner, rawModel);

    // Apply Function Annotation Rules
    GenericRuleReasoner annotationReasoner = new GenericRuleReasoner(Rule.parseRules(rules));
    InfModel infModel = ModelFactory.createInfModel(annotationReasoner, preprocessedModel);
    Model annotationModel = infModel.getDeductionsModel();

    System.out.println(">>>>");
    for(Statement stmt : annotationModel.listStatements().toSet()) {
      System.out.println(stmt);
    }
     
    RDFDataMgr.write(new FileWriter(new File(fileOut)), rawModel.union(annotationModel), Lang.TURTLE);

  }


  /**
   * Returns the Forward Chaining Rules for Circuit Preprocessing.
   */
  public static String getPreprocessRules() throws java.io.IOException {
    
    return "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.\n" +
           "@prefix wikidata: <https://www.wikidata.org/wiki/> .\n" +
           "@prefix wikidata-prop: <https://www.wikidata.org/wiki/Property:> .\n" +

           // (A)->(B)  => (B)->(A)
           "[electricalSymmetry: (?a wikidata-prop:P2789 ?b) -> (?b wikidata-prop:P2789 ?a)]\n" +

           // (A)-(Junction)-(C) => (A)-(C)
           "[bypassJunctions: (?a wikidata-prop:P2789 ?junction), (?junction wikidata-prop:P2789 ?c), (?junction rdf:type wikidata:Q5357725) -> (?a wikidata-prop:P2789 ?c)]\n" +

           // (A)->(P:Port)-(C) => (A)-(C)
           "[resolvePorts: (?owner wikidata-prop:P527 ?port), (?port rdf:type wikidata:Q947546), (?a wikidata-prop:P2789 ?port) -> (?a wikidata-prop:P2789 ?owner)]";

  }


  /**
   * Returns the Content of all Rule Files Concatinated to a String.
   */
  public static String loadRules() throws java.io.IOException {
    
    File ruleFolder = new File(Paths.get(".", "rules").toString());
    String[] ruleList = ruleFolder.list();
    String rules = "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.\n" +
                   "@prefix wikidata: <https://www.wikidata.org/wiki/> .\n" +
                   "@prefix wikidata-prop: <https://www.wikidata.org/wiki/Property:> .\n";

    for(String ruleFile : ruleList) {
      rules += Files.readString(Paths.get(".", "rules", ruleFile)) + "\n";
    }

    return rules;
  }


  public static CommandLine parseCLI(String[] args) throws ParseException {

    Options options = new Options();
    options.addOption("i", "input", true, "Input File");
    options.addOption("o", "output", true, "Output File");
    CommandLineParser gnuParser = new GnuParser();

    return gnuParser.parse(options, args);
  }

}
