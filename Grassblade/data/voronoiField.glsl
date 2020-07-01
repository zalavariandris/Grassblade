#ifdef GL_ES
precision mediump float;
precision mediump int;
#endif


uniform sampler2D seedCoordTex;
uniform sampler2D seedColorTex;
varying vec4 vertTexCoord;

void main(){
	vec2 fragCoord = vec2(vertTexCoord.x, vertTexCoord.y)-vec2(1.0/512*0.5);
	vec2 seedCoord = texture2D(seedCoordTex, fragCoord).st;
	vec3 seedColor = texture2D(seedColorTex, seedCoord).rgb;
	gl_FragColor = vec4(seedColor, 1);
}