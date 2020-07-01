static int log2(int x)
{
    return (int) (Math.log(x) / Math.log(2));
}

PShape square;
PointsEditor pointsEditor;
Paper paper;
//PShader floodFillShader;
//PShader coordShader;
PShader distanceFieldShader;
PShader voronoiFieldShader;

int N = 256;
//int MAX_PASS_STEPS = log2(N);

//PImage seedImage;
//PGraphics buffer1;
PGraphics seedColorFbo;
//PGraphics floodFillFbo;
PGraphics distanceFieldFbo;
PGraphics voronoiFieldFbo;

static int CELL_SIZE = 256;


JFA jfa;

void setup() {
  
  size(1300, 1600, P3D);
  noSmooth();
  hint(DISABLE_DEPTH_MASK);
  hint(DISABLE_TEXTURE_MIPMAPS);
  noStroke();
  //noLoop();
  
  /*  */
  //floodFillShader = loadShader("jumpFloodFill.glsl", "passthrough.vert");
  //floodFillShader.set("texOffset", 1.0/N, 1.0/N);
  //coordShader = loadShader("coord.glsl", "passthrough.vert");
  distanceFieldShader = loadShader("distanceField.glsl","passthrough.vert");
  voronoiFieldShader = loadShader("voronoiField.glsl", "passthrough.vert");
  
  //seedImage = loadImage("points.png");
  
  seedColorFbo = createGraphics(N, N, P3D);
  ((PGraphicsOpenGL)seedColorFbo).textureSampling(POINT); // does not work with min_filter
  
  //floodFillFbo = createGraphics(N, N, P3D);
  //((PGraphicsOpenGL)floodFillFbo).textureSampling(POINT);
  //buffer1 = createGraphics(N, N, P3D);
  //((PGraphicsOpenGL)buffer1).textureSampling(POINT);
  
   distanceFieldFbo = createGraphics(N, N, P3D);
  ((PGraphicsOpenGL)distanceFieldFbo).textureSampling(POINT);
  
  voronoiFieldFbo = createGraphics(N, N, P3D);
  ((PGraphicsOpenGL)voronoiFieldFbo).textureSampling(POINT);
  
  // quad
  square = createShape(RECT, 0, 0, N, N);
  pointsEditor = new PointsEditor();
  paper = new Paper(N, N);
  
  jfa = new JFA(N);
}
int _mouseX;
int _mouseY;
int k=0;
void draw() {
    paper.update();
    // fill initial colors
    seedColorFbo.beginDraw();
    seedColorFbo.background(0);
    seedColorFbo.image(paper.graphics, 0,0);
    seedColorFbo.endDraw();
    
    jfa.floodCoords(seedColorFbo);
    
    //// Distance Field Map
    distanceFieldShader.set("seedCoordTex", jfa.coordsFbo);
    distanceFieldFbo.beginDraw();
    distanceFieldFbo.noSmooth();
    distanceFieldFbo.hint(DISABLE_TEXTURE_MIPMAPS);
    distanceFieldFbo.shader(distanceFieldShader);
    distanceFieldFbo.shape(square);
    distanceFieldFbo.endDraw();
    
    // Voronoi Field Map
    voronoiFieldShader.set("seedCoordTex", jfa.coordsFbo);
    voronoiFieldShader.set("seedColorTex", seedColorFbo);
    voronoiFieldFbo.beginDraw();
    voronoiFieldFbo.noSmooth();
    voronoiFieldFbo.hint(DISABLE_TEXTURE_MIPMAPS);
    voronoiFieldFbo.shader(voronoiFieldShader);
    voronoiFieldFbo.shape(square);
    voronoiFieldFbo.endDraw();


  // display
  background(255);
  // display source image
  image(seedColorFbo, 0, 0, CELL_SIZE, CELL_SIZE);
  
  //display fbo
  //image(floodFillFbo, CELL_SIZE, CELL_SIZE, CELL_SIZE, CELL_SIZE);
  //image(buffer1, 0, 2*CELL_SIZE, CELL_SIZE,CELL_SIZE);
  
  // display distance field
  image(distanceFieldFbo, 0, 2*CELL_SIZE, CELL_SIZE, CELL_SIZE);
  image(voronoiFieldFbo, CELL_SIZE, 2*CELL_SIZE, CELL_SIZE, CELL_SIZE);
  
  fill(0,255,0);
  text("N:              "+N, 0,20);
  text("MAX_PASS_STEPS: "+jfa.MAX_PASS_STEPS, 0,40);
  text("selection: "+pointsEditor.selectedIndex, 0,60);
  text("fps: "+frameRate, 0,80);
  
  
  //image(pass2, 256, 512, 256, 256);
  //image(pass3, 512, 512, 256, 256);
  //pointsEditor.draw();
  
  image(jfa.coordsFbo, 600, 600);
  image(jfa.bufferFbo, 600, 800);
}

void keyPressed(){
  if (keyCode == UP){
    jfa.MAX_PASS_STEPS+=1;
    print("MAX_PASS_STEPS", jfa.MAX_PASS_STEPS);
  }
  if (keyCode == DOWN){
    jfa.MAX_PASS_STEPS-=1;
    print("MAX_PASS_STEPS", jfa.MAX_PASS_STEPS);
  }
}
