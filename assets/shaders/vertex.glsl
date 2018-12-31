// modified from https://discourse.panda3d.org/t/shadows-direction-parameters-and-inputs-in-glsl/15300/4
#version 330

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;

in vec4 vertex;
in vec3 normal;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;

out vec4 vpos;
out vec3 norm;
//out vec4 shad[1];
out vec4 vcolor;
out vec2 tex_coord;

void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * vertex;
  vpos = p3d_ModelViewMatrix * vertex;
  norm = normalize(p3d_NormalMatrix * normal);
  vcolor = p3d_Color;
  tex_coord = p3d_MultiTexCoord0;
}