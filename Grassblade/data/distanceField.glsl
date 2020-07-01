#ifdef GL_ES
precision mediump float;
precision mediump int;
#endif

#define M_PI 3.1415926535897932384626433832795

uniform sampler2D seedCoordTex;
varying vec4 vertTexCoord;

void main(){
	vec2 fragCoord = vec2(vertTexCoord.x, vertTexCoord.y);
	vec2 seedCoord = texture2D(seedCoordTex, fragCoord).xy;

	vec2 dir = normalize(fragCoord - seedCoord);
	float angle = (atan(dir.y, dir.x)+M_PI)/(M_PI*2);
	float dist = length(fragCoord - seedCoord)*3.0;

	gl_FragColor = vec4(dist, angle, 0, 1);
}