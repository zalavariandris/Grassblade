#ifdef GL_ES
precision mediump float;
precision mediump int;
#endif

uniform sampler2D mask;
varying vec4 vertTexCoord;

void main(){
	vec4 mask = texture2D(mask, vertTexCoord.st);
	if(mask.xyz==vec3(0,0,0)){
		gl_FragColor = vec4(0,0,0,1);
	}else{
		gl_FragColor = vec4(vertTexCoord.st, 0, 1);
	}
}
