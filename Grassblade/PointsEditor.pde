public class PointsEditor{
  ArrayList<PVector> positions;
  ArrayList<Integer> colors;
  
  int hoveredIndex=-1;
  int selectedIndex=-1;
  boolean mouseDown;
  int _mouseX;
  int _mouseY;
  boolean mouseClick;
  PointsEditor(){
    mouseDown = false;
    positions = new ArrayList<PVector>();
    colors = new ArrayList<Integer>();
    print("PointsEditor constructor");
  }
  
  void updateMouseEvents(){
    if(!mousePressed){
      int hitIndex = hitTest(mouseX, mouseY);
      
      if(hitIndex!=hoveredIndex){
        if(hoveredIndex>=0){
          onMouseLeave(hoveredIndex);
        }
        hoveredIndex = hitIndex;
        if(hitIndex>=0){
          onMouseEnter(hitIndex);
        }
      }
      hoveredIndex = hitIndex;
      if(_mouseX!=mouseX || _mouseY!=mouseY){
        _mouseX = mouseX;
        _mouseY = mouseY;
        onMouseMove();
      }
    }else{
      if(_mouseX!=mouseX || _mouseY!=mouseY){
        _mouseX = mouseX;
        _mouseY = mouseY;
        onMouseDrag();
      }
    }
    if(mouseDown && !mousePressed){
      onMousePress();
    }
    mouseDown = mousePressed;
  }
  
  void onMousePress(){
    int hitIndex = hitTest(mouseX, mouseY);
    if(hitIndex<0 && mouseButton==LEFT){
      positions.add(new PVector(mouseX, mouseY));
      colors.add(color(random(255),random(255),random(255)));
      
      selectedIndex = positions.size()-1;
      print("add", selectedIndex);
    }else{
      if(selectedIndex == hitIndex){
        colors.set(selectedIndex, color(random(255), random(255), random(255)));
      }else{
        selectedIndex = hitIndex;
      }
      
    }
    
    if(hitIndex>=0 && mouseButton==RIGHT){
      positions.remove(hitIndex);
      colors.remove(hitIndex);
    }

  }
  
  void onMouseEnter(int index){
    print("enter", index);
  }
  
  void onMouseLeave(int index){
    print("leave", index);
  }
  
  void onMouseMove(){

  }
  
  void onMouseDrag(){
    //if(selectedIndex>=0 || selectedIndex<positions.size()){
    //  positions.get(selectedIndex).x = mouseX;
    //  positions.get(selectedIndex).y = mouseY;
    //}
  }
  
  void draw(){
    updateMouseEvents();
    for(int i=0; i<positions.size(); i++){
      PVector point = positions.get(i);
      if(i==hoveredIndex || i==selectedIndex){
        stroke(255);
      }else{
        noStroke();
      }
      fill(colors.get(i));
      circle(point.x, point.y, 10);
    }
  }
  
  int hitTest(float x, float y){
    PVector pos = new PVector(x, y);
    for(int i=0; i<positions.size(); i++){
      PVector point = positions.get(i);
      if(PVector.dist(point, pos)<10){
        return i;
      }
    }
    return -1;
  }
}
