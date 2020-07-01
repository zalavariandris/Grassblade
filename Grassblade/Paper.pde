public class Paper{
  PGraphics graphics;
  int _mouseX;
  int _mouseY;
  
  Paper(int width, int height){
    _mouseX = mouseX;
    _mouseY = mouseY;
    graphics = createGraphics(width, height, P3D);
    graphics.beginDraw();
    graphics.background(0);
    graphics.endDraw();
  }
  
  void update(){
    graphics.beginDraw();
    if( (_mouseX!=mouseX || mouseX!=_mouseY) && mousePressed){
      print(keyCode);
      if(keyPressed && keyCode==ALT){
        graphics.stroke(0);
        graphics.strokeWeight(50);
      }else{
        graphics.stroke(255);
        graphics.strokeWeight(3);
      }
      graphics.line(
        (float)_mouseX/CELL_SIZE*N+0.5,
        (float)_mouseY/CELL_SIZE*N+0.5,
        (float)mouseX/CELL_SIZE*N+0.5,
        (float)mouseY/CELL_SIZE*N+0.5
       );
    }
    _mouseX = mouseX;
    _mouseY = mouseY;
    graphics.endDraw();
  }
}
