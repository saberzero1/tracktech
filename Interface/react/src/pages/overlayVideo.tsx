/*

This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Project course.
© Copyright Utrecht University (Department of Information and Computing Sciences)

 */

import { Component } from 'react'

import { Overlay } from '../components/overlay'

export class OverlayVideo extends Component {
  render() {
    return <Overlay
        cameraId={"test"}
        onButtonClick={() => alert('resize')}
        key={'testvid'}
        autoplay={true}
        controls={true}
        width={300}
        height={300}
        sources={[{ src: 'http://localhost:80/testvid.m3u8' }]}
        showBoxes="All"
    />
  }
}