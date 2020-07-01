#ifdef GL_ES
precision mediump float;
precision mediump int;
#endif

uniform float offset;
uniform sampler2D seedCoordTex;
varying vec4 vertTexCoord;
uniform vec2 texOffset;

void main(){
	vec2 fragCoord = vec2(vertTexCoord.x, vertTexCoord.y);
	float stepWidth = 1.0/8.0;

	// step 1
	vec2 bestNormal = vec2(0, 0);
	float bestDistance = 9999;
	vec2 bestCoord = vec2(0,0);
	vec3 bestColor = vec3(0,0,0);

	// vec2 pixelSize = vec2(1.0/8);
	vec2 pixelSize = texOffset;

	for(int y=-1;y<=1;++y){
		for(int x=-1; x<=1;++x){
			vec2 sampleCoord = fragCoord+vec2(x, y)*pixelSize*offset;
			vec2 seedCoord = texture2D(seedCoordTex, sampleCoord).xy;

			float dist = length(seedCoord-fragCoord);
			if(  (seedCoord.x!=0.0 || seedCoord.y!=0.0) && dist<=bestDistance )
			{
				bestDistance = dist;
				bestCoord = seedCoord;
			}
		}
	}

	// bestCoord = texture2D(seedCoordTex, fragCoord).xy;
	gl_FragColor = vec4(bestCoord.x, bestCoord.y, 0, 1);
}
