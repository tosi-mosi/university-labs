/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package crypto.crypto_lab1;
import java.io.FileReader;
import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import static java.lang.System.*;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.Map;
/**
 *
 * @author dimas
 */


class FileContentReader
        {
   protected final String fileContent;
   
   FileContentReader(String FilePath, String encoding){
       StringBuilder text = new StringBuilder();
        try{
             //System.out.print((new FileReader("C:\\Users\\dimas\\Desktop\\java\\lab1_resources\\TEXT")).getEncoding());
             InputStreamReader isr = new InputStreamReader(new FileInputStream(FilePath), encoding);
             BufferedReader br = new BufferedReader(isr);
             
             String currentLine;
             while((currentLine = br.readLine())!=null){
                 text.append(currentLine).append("\n");
             }
        }catch(Exception e){
            e.printStackTrace();
        }
        fileContent = text.toString();
   }
   
   String getFileContent(){
       return fileContent;
   }   
}

class Calculator{

  private final String rusAlphabetWithWhitespace = "абвгдеЄжзийклмнопрстуфхцчшщъыьэю€ ";
  private int alphabetLength, alphabetLengthNoSpace;
  private LinkedHashMap<String, Double> freqMapBigramsCrossingWithSpace, freqMapBigramsCrossingWithoutSpace,
          freqMapBigramsNonCrossingWithSpace, freqMapBigramsNonCrossingWithoutSpace, freqMapMonograms, freqMapMonogramsNoSpace;
  private double H1Space, H1NoSpace, H2CrossingNoSpace, H2CrossingSpace, H2NonCrossingNoSpace, H2NonCrossingSpace, H0;
  private double Redundancy;
  
  private String text;
  private String textWithoutSpaces;
  
  Calculator(String fileContent){// 1 or 2
    alphabetLength = rusAlphabetWithWhitespace.length();
    //out.println(text);
    text = fileContent.toLowerCase().replaceAll("[^абвгдеЄжзийклмнопрстуфхцчшщъыьэю€ ]", "");
    //out.println(text);        
    
    textWithoutSpaces = text.replace(" ", "");
    freqMapBigramsCrossingWithSpace = new LinkedHashMap<String, Double>();
    freqMapBigramsCrossingWithoutSpace = new LinkedHashMap<String, Double>();
    freqMapBigramsNonCrossingWithSpace = new LinkedHashMap<String, Double>();
    freqMapBigramsNonCrossingWithoutSpace = new LinkedHashMap<String, Double>();
    freqMapMonograms = new LinkedHashMap<String, Double>();
    freqMapMonogramsNoSpace = new LinkedHashMap<String, Double>();
    H0 = Math.log(alphabetLength)/Math.log(2);

    for(int i=0;i<alphabetLength;i++){
        //out.print(alphabetLength);
        rusAlphabetWithWhitespace.charAt(i);
        freqMapMonograms.put(Character.toString(rusAlphabetWithWhitespace.charAt(i)), 0.0);
        if(rusAlphabetWithWhitespace.charAt(i)!=' '){
            freqMapMonogramsNoSpace.put(Character.toString(rusAlphabetWithWhitespace.charAt(i)), 0.0);}
    }
    
    for(int i=0;i<alphabetLength;i++){
        for(int j=0;j<alphabetLength;j++){
          //rusAlphabetWithWhitespace.charAt(i);
          freqMapBigramsCrossingWithSpace.put(Character.toString(rusAlphabetWithWhitespace.charAt(i))+Character.toString(rusAlphabetWithWhitespace.charAt(j)), 0.0);
          freqMapBigramsNonCrossingWithSpace.put(Character.toString(rusAlphabetWithWhitespace.charAt(i))+Character.toString(rusAlphabetWithWhitespace.charAt(j)), 0.0);
          //step over whitespaces
          if(i!=alphabetLength-1 && j!=alphabetLength-1){
              freqMapBigramsCrossingWithoutSpace.put(Character.toString(rusAlphabetWithWhitespace.charAt(i))+Character.toString(rusAlphabetWithWhitespace.charAt(j)), 0.0);
              freqMapBigramsNonCrossingWithoutSpace.put(Character.toString(rusAlphabetWithWhitespace.charAt(i))+Character.toString(rusAlphabetWithWhitespace.charAt(j)), 0.0);
          }
        }
    }
    calculateMonogramsFrequencies();
    calculateBigramsFrequencies();
    calculateH1H2Red();
  }

  private void calculateMonogramsFrequencies() {
      for(int i=0;i<text.length();i++){
          String tmp_monogram = Character.toString(text.charAt(i));
          double tmp_freq = freqMapMonograms.get(tmp_monogram);
          freqMapMonograms.put(tmp_monogram, tmp_freq+1.0/text.length());
      }
      for(int i=0;i<textWithoutSpaces.length();i++){
          String tmp_monogram = Character.toString(textWithoutSpaces.charAt(i));
          double tmp_freq = freqMapMonogramsNoSpace.get(tmp_monogram);
          freqMapMonogramsNoSpace.put(tmp_monogram, tmp_freq+1.0/textWithoutSpaces.length());
      }
  }
  
  private void calculateBigramsFrequencies(){
      //calculate with spaces
      for(int i=0;i<text.length()-1;i++){
          
          String tmpCrossingBigram = text.substring(i, i+2);
          double tmpCrossingFreq = freqMapBigramsCrossingWithSpace.get(tmpCrossingBigram);
          //calculate crossing brigrams
          freqMapBigramsCrossingWithSpace.put(tmpCrossingBigram, tmpCrossingFreq+1.0/(text.length()-1));
          //calculate non crossing bigrams
          if(i%2 == 0){
              freqMapBigramsNonCrossingWithSpace.put(tmpCrossingBigram, tmpCrossingFreq+1.0/(text.length()/2));
          }
      }
      //calculate without spaces
      for(int i=0;i<textWithoutSpaces.length()-1;i++){
          String tmpCrossingBigram = textWithoutSpaces.substring(i, i+2);
          double tmpCrossingFreq = freqMapBigramsCrossingWithoutSpace.get(tmpCrossingBigram);
          //calculate crossing brigrams
          freqMapBigramsCrossingWithoutSpace.put(tmpCrossingBigram, tmpCrossingFreq+1.0/(textWithoutSpaces.length()-1));
          //calculate non crossing bigrams
          if(i%2 == 0){
              freqMapBigramsNonCrossingWithoutSpace.put(tmpCrossingBigram, tmpCrossingFreq+1.0/(text.length()/2));
          }
      }
  }
  
  private void calculateH1H2Red(){
      //H1
      for(Map.Entry<String, Double> entry : freqMapMonograms.entrySet()){
          H1Space -= entry.getValue() == 0.0 ? 0 : entry.getValue()*Math.log(entry.getValue())/Math.log(2.0);
      }
      for(Map.Entry<String, Double> entry : freqMapMonogramsNoSpace.entrySet()){
          H1NoSpace -= entry.getValue() == 0.0 ? 0 : entry.getValue()*Math.log(entry.getValue())/Math.log(2.0);
      }
      //H2
      for(Map.Entry<String, Double> entry : freqMapBigramsCrossingWithSpace.entrySet()){
          H2CrossingSpace -= entry.getValue() == 0.0 ? 0 : entry.getValue()*Math.log(entry.getValue())/Math.log(2.0);
      }
      H2CrossingSpace = H2CrossingSpace/2;
      
      for(Map.Entry<String, Double> entry : freqMapBigramsCrossingWithoutSpace.entrySet()){
          H2CrossingNoSpace -= entry.getValue() == 0.0 ? 0 : entry.getValue()*Math.log(entry.getValue())/Math.log(2.0);
      }
      H2CrossingNoSpace = H2CrossingNoSpace/2;
      
      for(Map.Entry<String, Double> entry : freqMapBigramsNonCrossingWithSpace.entrySet()){
          H2NonCrossingSpace -= entry.getValue() == 0.0 ? 0 : entry.getValue()*Math.log(entry.getValue())/Math.log(2.0);
      }
      H2NonCrossingSpace /=2;
      
      for(Map.Entry<String, Double> entry : freqMapBigramsNonCrossingWithoutSpace.entrySet()){
          H2NonCrossingNoSpace -= entry.getValue() == 0.0 ? 0 : entry.getValue()*Math.log(entry.getValue())/Math.log(2.0);
      }
      H2NonCrossingNoSpace/=2;
      
  }
  
  public void displayEntropy(){
        System.out.println(String.format("H1 with spaces = %f, Redundancy = %f\n"
                + "H1 without spaces = %f, Redundancy = %f\n"
                + "H2 crossing and with spaces = %f, Redundancy = %f\n"
                + "H2 crossing and without spaces = %f, Redundancy = %f\n"
                + "H2 noncrossing with spaces = %f, Redundancy = %f\n"
                + "H2 noncrossing without spaces = %f, Redundancy = %f\n",
                H1Space,1-H1Space/H0,
                H1NoSpace,1-H1NoSpace/H0,
                H2CrossingSpace,1-H2CrossingSpace/H0,
                H2CrossingNoSpace,1-H2CrossingNoSpace/H0,
                H2NonCrossingSpace,1-H2NonCrossingSpace/H0,
                H2NonCrossingNoSpace,1-H2NonCrossingNoSpace/H0)); 
  }
  
  public void displayNgramsFrequencies(Map<String, Double> freqMap){
        for(Map.Entry<String, Double> entry : freqMap.entrySet()){
            out.println("\'"+entry.getKey()+ "\':"+entry.getValue()+",");
        }
  }

  public void displayBigramsNonCrossingWithoutSpace(){
      /*out.println("\t„астоты не пересекающихс€ биграмм в тексте без пробелов");
      char check_for_new_line = 'а';
      for(int i=0;i<rusAlphabetWithWhitespace.length()-1;i++){
          out.format("\t  [%c]", rusAlphabetWithWhitespace.charAt(i));
      }
      out.print("\n[a]\t");
        for(Map.Entry<String, Double> entry : freqMapBigramsNonCrossingWithoutSpace.entrySet()){
            if(check_for_new_line != entry.getKey().charAt(0)){
                check_for_new_line = entry.getKey().charAt(0);
                out.format("\n[%c]\t", check_for_new_line);
            }
          out.format("%.5f\t", entry.getValue()); 
        }
        out.print("\n\n");*/
      //get top 5 bigrams
   
    for(int j=0;j<5;j++){
        Double max= 0.0;
        String maxBi = "";
        for(Map.Entry<String, Double> entry : freqMapBigramsNonCrossingWithoutSpace.entrySet()){
           if(entry.getValue() > max){
               max = entry.getValue();
               maxBi = entry.getKey();
           }
        }
        freqMapBigramsNonCrossingWithoutSpace.remove(maxBi);
        System.out.println(String.format("bi %s, fr = %f", maxBi, max));
    }
      System.out.println(freqMapBigramsNonCrossingWithoutSpace.get("ен"));
  }
  
    public void displayBigramsCrossingWithoutSpace(){
        out.println("\t„астоты пересекающихс€ биграмм в тексте без пробелов");
        char check_for_new_line = 'а';
      for(int i=0;i<rusAlphabetWithWhitespace.length()-1;i++){
          out.format("\t  [%c]", rusAlphabetWithWhitespace.charAt(i));
      }
      out.print("\n[a]\t");
        for(Map.Entry<String, Double> entry : freqMapBigramsCrossingWithoutSpace.entrySet()){
            if(check_for_new_line != entry.getKey().charAt(0)){
                check_for_new_line = entry.getKey().charAt(0);
                out.format("\n[%c]\t", check_for_new_line);
            }
          out.format("%.5f\t", entry.getValue()); 
        }
        out.print("\n\n");
  }
    
    public void displayBigramsCrossingWithSpace(){
      out.println("\t„астоты пересекающихс€ биграмм в тексте с пробелами");
      char check_for_new_line = 'а';
      for(int i=0;i<rusAlphabetWithWhitespace.length();i++){
          out.format("\t  [%c]", rusAlphabetWithWhitespace.charAt(i));
      }
      out.print("\n[a]\t");
        for(Map.Entry<String, Double> entry : freqMapBigramsCrossingWithSpace.entrySet()){
            if(check_for_new_line != entry.getKey().charAt(0)){
                check_for_new_line = entry.getKey().charAt(0);
                out.format("\n[%c]\t", check_for_new_line);
            }
          out.format("%.5f\t", entry.getValue()); 
        }
        out.print("\n\n");
  }
        
    public void displayBigramsNonCrossingWithSpace(){
      out.println("\t „астоты не пересекающихс€ биграмм в текстe c пробелaми");
      char check_for_new_line = 'а';
      for(int i=0;i<rusAlphabetWithWhitespace.length();i++){
          out.format("\t  [%c]", rusAlphabetWithWhitespace.charAt(i));
      }
      out.print("\n[a]\t");
        for(Map.Entry<String, Double> entry : freqMapBigramsNonCrossingWithSpace.entrySet()){
            if(check_for_new_line != entry.getKey().charAt(0)){
                check_for_new_line = entry.getKey().charAt(0);
                out.format("\n[%c]\t", check_for_new_line);
            }
          out.format("%.5f\t", entry.getValue()); 
        }
        out.print("\n\n");
  }
  
  public void displayMonogramsWithSpaceFrequencies(){
      displayNgramsFrequencies(freqMapMonograms);
      
  }
  
   public void displayMonogramsWithoutSpaceFrequencies(){
      displayNgramsFrequencies(freqMapMonogramsNoSpace);
  } 
}

public class Main {
    /**
     * @param args the command line arguments
     **/
    
   
    
    public static void main(String[] args) throws UnsupportedEncodingException {
        
        //run: cd C:\Users\dimas\Desktop\java\crypto_lab1\build\classes\java\main 
        //     java crypto.crypto_lab1.Main
        
        //FILENAME       ENCODING
        //file3.txt  -   utf-8          
        //TEXT       -   1251
        
        String data = new FileContentReader("C:\\Users\\dimas\\Desktop\\crypto_labs\\lab1\\lab1_resources\\file3.txt", "utf-8").getFileContent();
        Calculator nfc = new Calculator(data);
                        
        nfc.displayMonogramsWithoutSpaceFrequencies();
//        nfc.displayMonogramsWithSpaceFrequencies();
//        nfc.displayBigramsCrossingWithSpace();
       // nfc.displayBigramsNonCrossingWithSpace();
//        nfc.displayBigramsCrossingWithoutSpace();
        //nfc.displayBigramsNonCrossingWithoutSpace();
//        
//        nfc.displayEntropy();
        //try{whenReadWithBufferedReader_thenCorrect();}catch(Exception e){e.printStackTrace();}
    }

    public Main() {
    }
}
