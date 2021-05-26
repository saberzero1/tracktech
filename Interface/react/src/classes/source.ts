/*

This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Project course.
© Copyright Utrecht University (Department of Information and Computing Sciences)

 */

/**
 * Defines the properties of a single camera feed
 * Contians an identifier, a name and the stream URL
 */
export type source = {
  id: string
  name: string
  srcObject: { src: string; type: string }
}