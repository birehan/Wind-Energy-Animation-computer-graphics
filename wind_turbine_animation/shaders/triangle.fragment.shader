
# version 330

in vec2 v_texture;
in vec3 TexCoords;

out vec4 out_color;
out vec4 FragColor;

uniform sampler2D s_texture;
uniform samplerCube skybox;

void main()
{
    FragColor = texture(s_texture, v_texture);

    FragColor = texture(skybox, TexCoords);

}

// #version 330 core
// out vec4 FragColor;
//
// in vec3 TexCoords;
//
// uniform samplerCube skybox;
//
// void main()
// {
//     FragColor = texture(skybox, TexCoords);
// }
