#version 330
in vec2 v_q;in float v_radius;in vec3 v_color;
uniform float u_weight;
out vec4 out_color;
void main(){float d=length(v_q)/v_radius;out_color=vec4(v_color*exp(-d*d*2.)*u_weight,1.);}
