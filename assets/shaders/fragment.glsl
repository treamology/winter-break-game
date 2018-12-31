// modified from https://discourse.panda3d.org/t/shadows-direction-parameters-and-inputs-in-glsl/15300/4
#version 330

uniform sampler2D p3d_Texture0;

uniform struct {
  vec4 ambient;
} p3d_LightModel;

uniform struct {
  vec4 ambient;
  vec4 diffuse;
  vec4 emission;
  vec3 specular;
  float shininess;

  // These properties are new in 1.10.
  vec4 baseColor;
  float roughness;
  float metallic;
  float refractiveIndex;
} p3d_Material;

uniform struct {
  vec4 color;
  vec4 position;
  vec4 diffuse;
  vec4 specular;
  vec3 attenuation;
  vec3 spotDirection;
  float spotCosCutoff;
  float spotExponent;
  samplerCubeShadow shadowMap;
  mat4 shadowViewMatrix;
} p3d_LightSource[1];

uniform vec4 cam_pos;

in vec4 vpos;
in vec3 norm;
//in vec4 shad[1];
in vec4 vcolor;
in vec2 tex_coord;

out vec4 p3d_FragData[4];

void main() {
  p3d_FragData[0] = p3d_LightModel.ambient * p3d_Material.ambient;

  for (int i = 0; i < p3d_LightSource.length(); ++i) {
    vec3 diff = p3d_LightSource[i].position.xyz - vpos.xyz * p3d_LightSource[i].position.w;
    vec3 L = normalize(diff);
    vec3 E = vec3(normalize(-vpos));
    vec3 R = normalize(E + L);
    vec4 diffuse = clamp(p3d_Material.diffuse * max(dot(norm, L), 0), 0, 1) * p3d_LightSource[i].color;
    vec4 specular = vec4(p3d_Material.specular, 1) * pow(max(dot(R, norm), 0), p3d_Material.shininess) * p3d_LightSource[i].color;

    float spotEffect = dot(normalize(p3d_LightSource[i].spotDirection), -L);
    //diffuse *= textureProj(p3d_LightSource[i].shadowMap, p3d_LightSource[i].shadowViewMatrix * vpos);
    if (spotEffect > p3d_LightSource[i].spotCosCutoff) {
      diffuse *= pow(spotEffect, p3d_LightSource[i].spotExponent);
      diffuse *= texture(p3d_LightSource[i].shadowMap, p3d_LightSource[i].shadowViewMatrix * vpos);
      p3d_FragData[0] += (diffuse + specular) / dot(p3d_LightSource[i].attenuation, vec3(1, length(diff), length(diff) * length(diff)));
    }
  }

  p3d_FragData[0] *= vcolor * texture(p3d_Texture0, tex_coord);
}