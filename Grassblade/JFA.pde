public class JFA{
  PShader JFAshader;
  PShader coordShader;
  
  int N;
  int MAX_PASS_STEPS;
  
  PGraphics coordsFbo;
  PGraphics bufferFbo;
  PShape square;
  public JFA(int N){
    this.N = N;
    this.MAX_PASS_STEPS = log2(N);
    JFAshader = loadShader("jumpFloodFill.glsl", "passthrough.vert");
    
    coordShader = loadShader("coord.glsl", "passthrough.vert");
    square = createShape(RECT, 0, 0, N, N);
    
    print(N);
    coordsFbo = createGraphics(N, N, P3D);
    bufferFbo = createGraphics(N, N, P3D);
    
  }
  
  public void floodCoords(PGraphics seedColorFbo){
    // Fill initial coords
    coordShader.set("mask", seedColorFbo);
    coordsFbo.beginDraw();
    coordsFbo.noSmooth();
    coordsFbo.shader(coordShader);
    coordsFbo.shape(square);
    coordsFbo.endDraw();
    
    // Jump Flood Fill
    for(int i=0; i<MAX_PASS_STEPS; i++){
      float offset = (float)Math.pow(2, log2(N) - i- 1);
      JFAshader.set("texOffset", 1.0/N, 1.0/N);
      JFAshader.set("offset", offset);
      JFAshader.set("seedCoordTex", coordsFbo);
      bufferFbo.beginDraw();
      bufferFbo.noSmooth();
      bufferFbo.hint(DISABLE_TEXTURE_MIPMAPS);
      bufferFbo.shader(JFAshader);
      bufferFbo.shape(square);
      bufferFbo.endDraw();
      
      // swap fbos
      PGraphics t = coordsFbo;
      coordsFbo = bufferFbo;
      bufferFbo = t;
    }
  } 
}
