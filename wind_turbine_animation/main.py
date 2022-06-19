import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr
from TextureLoader import load_texture
from ObjLoader import ObjLoader
import numpy as np
from camera import Camera
from PIL import Image
import os

cam = Camera()
WIDTH, HEIGHT = 1280, 720
lastX, lastY = WIDTH / 2, HEIGHT / 2
first_mouse = True

def mouse_look_clb(window, xpos, ypos):
    global lastX, lastY

    if first_mouse:
        lastX = xpos
        lastY = ypos

    xoffset = xpos - lastX
    yoffset = lastY - ypos

    lastX = xpos
    lastY = ypos

    cam.process_mouse_movement(xoffset, yoffset)

# the mouse enter callback function
def mouse_enter_clb(window, entered):
    global first_mouse

    if entered:
        first_mouse = False
    else:
        first_mouse = True

def loadCubemap(faces):

    for i in range(len(faces)):
        image = Image.open(faces[i])

        width, height = image.size
        image_data = image.convert('RGBA').tobytes()

        glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGBA, width, height, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, image_data)

    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)


skyboxVertices= [
        -1.0,  1.0, -1.0,
        -1.0, -1.0, -1.0,
         1.0, -1.0, -1.0,
         1.0, -1.0, -1.0,
         1.0,  1.0, -1.0,
        -1.0,  1.0, -1.0,

        -1.0, -1.0,  1.0,
        -1.0, -1.0, -1.0,
        -1.0,  1.0, -1.0,
        -1.0,  1.0, -1.0,
        -1.0,  1.0,  1.0,
        -1.0, -1.0,  1.0,

         1.0, -1.0, -1.0,
         1.0, -1.0,  1.0,
         1.0,  1.0,  1.0,
         1.0,  1.0,  1.0,
         1.0,  1.0, -1.0,
         1.0, -1.0, -1.0,

        -1.0, -1.0,  1.0,
        -1.0,  1.0,  1.0,
         1.0,  1.0,  1.0,
         1.0,  1.0,  1.0,
         1.0, -1.0,  1.0,
        -1.0, -1.0,  1.0,

        -1.0,  1.0, -1.0,
         1.0,  1.0, -1.0,
         1.0,  1.0,  1.0,
         1.0,  1.0,  1.0,
        -1.0,  1.0,  1.0,
        -1.0,  1.0, -1.0,

        -1.0, -1.0, -1.0,
        -1.0, -1.0,  1.0,
         1.0, -1.0, -1.0,
         1.0, -1.0, -1.0,
        -1.0, -1.0,  1.0,
         1.0, -1.0,  1.0
    ]
skyboxVertices = np.array(skyboxVertices, dtype=np.float32)

def getFileContents(filename):
    p = os.path.join(os.getcwd(), "shaders", filename)
    return open(p, 'r').read()

def main():
    projection = pyrr.matrix44.create_perspective_projection_matrix(45, 1280 / 720, 0.1, 100)

    # glfw callback functions
    def window_resize(window, width, height):
        nonlocal projection

        glViewport(0, 0, width, height)
        projection = pyrr.matrix44.create_perspective_projection_matrix(45, width / height, 0.1, 100)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

    # initializing glfw library
    if not glfw.init():
        raise Exception("glfw can not be initialized!")
    # creating the window
    window = glfw.create_window(1280, 720, "Wind Turbine Animation", None, None)

    # check if window was created
    if not window:
        glfw.terminate()
        raise Exception("glfw window can not be created!")

    # set window's position
    glfw.set_window_pos(window, 400, 200)

    # set the callback function for window resize
    glfw.set_window_size_callback(window, window_resize)
    # set the mouse position callback
    glfw.set_cursor_pos_callback(window, mouse_look_clb)
    # set the mouse enter callback
    glfw.set_cursor_enter_callback(window, mouse_enter_clb)

    glfw.make_context_current(window)

    # load here the 3d meshes
    glClearColor(0.5, 0.5, 0.5, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    vertex_src = getFileContents("triangle.vertex.shader")
    fragment_src = getFileContents("triangle.fragment.shader")
    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                            compileShader(fragment_src, GL_FRAGMENT_SHADER))

    # load 3d meshes
    blade_indices, blade_buffer = ObjLoader.load_model("objects/blade.obj")
    stand_indices, stand_buffer = ObjLoader.load_model("objects/stand1.obj")


    # VAO and VBO
    VAO = glGenVertexArrays(6)
    VBO = glGenBuffers(6)

    # blade VAO
    glBindBuffer(GL_ARRAY_BUFFER, VBO[1])
    glBufferData(GL_ARRAY_BUFFER, blade_buffer.nbytes, blade_buffer, GL_STATIC_DRAW)
    glBindVertexArray(VAO[1])

    # blade vertices
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, blade_buffer.itemsize * 8, ctypes.c_void_p(0))
    # blade textures
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, blade_buffer.itemsize * 8, ctypes.c_void_p(12))
    # blade normals
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, blade_buffer.itemsize * 8, ctypes.c_void_p(20))
    glEnableVertexAttribArray(2)

    # stand VAO
    glBindBuffer(GL_ARRAY_BUFFER, VBO[2])
    glBufferData(GL_ARRAY_BUFFER, stand_buffer.nbytes, stand_buffer, GL_STATIC_DRAW)
    glBindVertexArray(VAO[2])

    # stand vertices
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stand_buffer.itemsize * 8, ctypes.c_void_p(0))
    # stand textures
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stand_buffer.itemsize * 8, ctypes.c_void_p(12))
    # stand normals
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stand_buffer.itemsize * 8, ctypes.c_void_p(20))
    glEnableVertexAttribArray(2)

    # skybox VAO
    glBindBuffer(GL_ARRAY_BUFFER, VBO[0])
    glBufferData(GL_ARRAY_BUFFER, skyboxVertices.nbytes, skyboxVertices, GL_STATIC_DRAW)
    glBindVertexArray(VAO[0])

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
                          3 * skyboxVertices.itemsize, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    faces = [
        "images/sky_right.png",
        "images/sky_left.png",
        "images/sky_top.png",
        "images/sky_bottom.png",
        "images/sky_front.png",
        "images/sky_back.png"
    ]

    textures = glGenTextures(6)
    glBindTexture(GL_TEXTURE_CUBE_MAP, textures[0])

    load_texture("images/blade.jpg", textures[1])
    load_texture("images/stand.jpg", textures[2])

    loadCubemap(faces)

    # eye, target, up
    # view_skymap = pyrr.matrix44.create_look_at(pyrr.Vector3([1, 0, 0]), pyrr.Vector3([0, 0, 0]), pyrr.Vector3([0, 1, 0]))
    # view_turbine = pyrr.matrix44.create_look_at(pyrr.Vector3([0, 2, 16]), pyrr.Vector3([0, 0, 0]), pyrr.Vector3([0, 1, 0]))

    sky_box_pos = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, 0, 0]))
    blade_pos_1 = pyrr.matrix44.create_from_translation(pyrr.Vector3([-0.1, 1.45, 20]))
    stand_pos_1 = pyrr.matrix44.create_from_translation(pyrr.Vector3([0, -1.9, 20.3]))

    blade_pos_2 = pyrr.matrix44.create_from_translation(pyrr.Vector3([-3.1, 1.45, 15]))
    stand_pos_2 = pyrr.matrix44.create_from_translation(pyrr.Vector3([-3, -1.9, 15.3]))

    blade_pos_3 = pyrr.matrix44.create_from_translation(pyrr.Vector3([3.1, 1.45, 20]))
    stand_pos_3 = pyrr.matrix44.create_from_translation(pyrr.Vector3([3, -1.9, 20.3]))

    blade_pos_4 = pyrr.matrix44.create_from_translation(pyrr.Vector3([-3.1, 1.45, 25]))
    stand_pos_4 = pyrr.matrix44.create_from_translation(pyrr.Vector3([-3, -1.9, 25.3]))

    blade_pos_5 = pyrr.matrix44.create_from_translation(pyrr.Vector3([3.1, 1.45, 25]))
    stand_pos_5 = pyrr.matrix44.create_from_translation(pyrr.Vector3([3, -1.9, 25.3]))

    blade_pos_6 = pyrr.matrix44.create_from_translation(pyrr.Vector3([-3.1, 1.45, 10]))
    stand_pos_6 = pyrr.matrix44.create_from_translation(pyrr.Vector3([-3, -1.9, 10.3]))

    blade_pos_7 = pyrr.matrix44.create_from_translation(pyrr.Vector3([3.1, 1.45, 10]))
    stand_pos_7 = pyrr.matrix44.create_from_translation(pyrr.Vector3([3, -1.9, 10.3]))

    model_loc = glGetUniformLocation(shader, "model")
    proj_loc = glGetUniformLocation(shader, "projection")
    view_loc = glGetUniformLocation(shader, "view")

    while not glfw.window_should_close(window):
        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        view = cam.get_view_matrix()

        r_y = [[0.17463187, 0, 0.98463379, 0.],
               [0., 1., 0., 0.],
               [-0.98463379, 0., 0.17463187, 0.],
               [0., 0., 0., 1.]]
        rot_z = pyrr.Matrix44.from_z_rotation(0.8 * glfw.get_time())

        model = pyrr.matrix44.multiply(r_y, sky_box_pos)

        glUseProgram(shader)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

        glDepthMask(GL_FALSE)

        # draw skybox
        glBindVertexArray(VAO[0])
        glBindTexture(GL_TEXTURE_CUBE_MAP, textures[0])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
        glDrawArrays(GL_TRIANGLES, 0, 36)

        glDepthMask(GL_TRUE)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)


        model_blade_2 = pyrr.matrix44.multiply(rot_z, blade_pos_2)

        # draw blade 2
        glBindVertexArray(VAO[1])
        glBindTexture(GL_TEXTURE_2D, textures[1])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_blade_2)
        glDrawArrays(GL_TRIANGLES, 0, len(blade_indices))

        # draw stand 2
        glBindVertexArray(VAO[2])
        glBindTexture(GL_TEXTURE_2D, textures[2])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, stand_pos_2)
        glDrawArrays(GL_TRIANGLES, 0, len(stand_indices))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

        model_blade_3 = pyrr.matrix44.multiply(rot_z, blade_pos_3)

        # draw blade 3
        glBindVertexArray(VAO[1])
        glBindTexture(GL_TEXTURE_2D, textures[1])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_blade_3)
        glDrawArrays(GL_TRIANGLES, 0, len(blade_indices))

        # draw stand 3
        glBindVertexArray(VAO[2])
        glBindTexture(GL_TEXTURE_2D, textures[2])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, stand_pos_3)
        glDrawArrays(GL_TRIANGLES, 0, len(stand_indices))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

        model_blade_4 = pyrr.matrix44.multiply(rot_z, blade_pos_4)

        # draw blade 4
        glBindVertexArray(VAO[1])
        glBindTexture(GL_TEXTURE_2D, textures[1])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_blade_4)
        glDrawArrays(GL_TRIANGLES, 0, len(blade_indices))

        # draw stand 4
        glBindVertexArray(VAO[2])
        glBindTexture(GL_TEXTURE_2D, textures[2])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, stand_pos_4)
        glDrawArrays(GL_TRIANGLES, 0, len(stand_indices))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

        model_blade_5 = pyrr.matrix44.multiply(rot_z, blade_pos_5)

        # draw blade 5
        glBindVertexArray(VAO[1])
        glBindTexture(GL_TEXTURE_2D, textures[1])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_blade_5)
        glDrawArrays(GL_TRIANGLES, 0, len(blade_indices))

        # draw stand 5
        glBindVertexArray(VAO[2])
        glBindTexture(GL_TEXTURE_2D, textures[2])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, stand_pos_5)
        glDrawArrays(GL_TRIANGLES, 0, len(stand_indices))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

        model_blade_6 = pyrr.matrix44.multiply(rot_z, blade_pos_6)

        # draw blade 6
        glBindVertexArray(VAO[1])
        glBindTexture(GL_TEXTURE_2D, textures[1])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_blade_6)
        glDrawArrays(GL_TRIANGLES, 0, len(blade_indices))

        # draw stand 6
        glBindVertexArray(VAO[2])
        glBindTexture(GL_TEXTURE_2D, textures[2])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, stand_pos_6)
        glDrawArrays(GL_TRIANGLES, 0, len(stand_indices))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

        model_blade_7 = pyrr.matrix44.multiply(rot_z, blade_pos_7)

        # draw blade 7
        glBindVertexArray(VAO[1])
        glBindTexture(GL_TEXTURE_2D, textures[1])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_blade_7)
        glDrawArrays(GL_TRIANGLES, 0, len(blade_indices))

        # draw stand 7
        glBindVertexArray(VAO[2])
        glBindTexture(GL_TEXTURE_2D, textures[2])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, stand_pos_7)
        glDrawArrays(GL_TRIANGLES, 0, len(stand_indices))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

        model_blade_1 = pyrr.matrix44.multiply(rot_z, blade_pos_1)

        # draw blade 1
        glBindVertexArray(VAO[1])
        glBindTexture(GL_TEXTURE_2D, textures[1])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_blade_1)
        glDrawArrays(GL_TRIANGLES, 0, len(blade_indices))

        # draw stand 1
        glBindVertexArray(VAO[2])
        glBindTexture(GL_TEXTURE_2D, textures[2])
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, stand_pos_1)
        glDrawArrays(GL_TRIANGLES, 0, len(stand_indices))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

        glfw.swap_buffers(window)


    glfw.terminate()


main()

