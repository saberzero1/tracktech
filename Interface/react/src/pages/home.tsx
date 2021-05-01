/*

This program has been developed by students from the bachelor Computer Science at
Utrecht University within the Software Project course.
© Copyright Utrecht University (Department of Information and Computing Sciences)

 */

/*
  This component is the homepage of the website, which contains all the videoplayers,
  the option to select what bounding boxes to draw, a list of the cameras, and TODO: a list of tracked suspects
*/

import React from 'react'
import { Button, Card } from 'antd'
import { Layout } from 'antd'
import { PlusOutlined } from '@ant-design/icons'

import { Grid, source } from '../components/grid'
import { CameraCard } from '../components/cameraCard'

/** The selection modes for the bounding boxes */
export type indicator = 'All' | 'Selection' | 'None'

/** Data required to track an object (placeholder, TODO: implement tracking) */
type tracked = { id: number; name: string; image: string; data: string }
export function Home() {
  /** State containing all the camera sources */
  const [sources, setSources] = React.useState<source[]>()

  /** State containing which boundingboxes to draw */
  const [currentIndicator, setCurrentIndicator] = React.useState<indicator>(
    'All'
  )

  /** State containing the tracked objects */
  const [tracking, setTracking] = React.useState<tracked[]>([])

  /** State containing which camera currently is the primary camera */
  const [primary, setPrimary] = React.useState<string>()

  const selectionRef = React.useRef(0)

  React.useEffect(() => {
    //Read all the sources from the config file and create sources for the videoplayers
    fetch(process.env.PUBLIC_URL + '/config.json').then((text) =>
      text.json().then((json) => {
        var nexId = 0
        setSources(
          json.map((stream) => ({
            id: nexId++,
            name: stream.Name,
            srcObject: {
              src: stream.Forwarder,
              type: stream.Type
            }
          }))
        )
      })
    )
  }, [])

  return (
    <Layout.Content
      style={{
        display: 'grid',
        gridTemplateColumns: '1fr 4fr',
        gridAutoRows: '100%',
        overflow: 'hidden'
      }}
    >
      <div
        style={{
          padding: '5px',
          overflowY: 'auto',
          display: 'grid',
          gap: '5px'
        }}
      >
        <Card
          //This card contains the buttons to change which boundingboxes are drawn
          bodyStyle={{ padding: '4px', display: 'flex' }}
          headStyle={{ padding: 0 }}
          size="small"
          title={
            <h2 style={{ margin: '0px 8px', fontSize: '20px' }}>Indicators</h2>
          }
        >
          <Button
            style={{ marginLeft: '4px' }}
            type={currentIndicator === 'All' ? 'primary' : 'default'}
            onClick={() => setCurrentIndicator('All')}
          >
            All
          </Button>
          <Button
            style={{ marginLeft: '4px' }}
            type={currentIndicator === 'Selection' ? 'primary' : 'default'}
            onClick={() => setCurrentIndicator('Selection')}
          >
            Selection
          </Button>
          <Button
            style={{ marginLeft: '4px' }}
            type={currentIndicator === 'None' ? 'primary' : 'default'}
            onClick={() => setCurrentIndicator('None')}
          >
            None
          </Button>
        </Card>

        <Card
          //This card contains the objects that are being tracked, TODO: implement tracking
          bodyStyle={{ padding: '4px' }}
          headStyle={{ padding: 0 }}
          size="small"
          title={
            <h2 style={{ margin: '0px 8px', fontSize: '20px' }}>Selection</h2>
          }
        >
          <div>
            <Button onClick={async () => await addSelection()}>+</Button>
          </div>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))',
              gridAutoRows: '100px'
            }}
          >
            {tracking &&
              tracking.map((tracked) => {
                var iterator = 0
                return (
                  <img
                    key={`image-${iterator++}`}
                    alt="tracked person"
                    onClick={() => removeSelection(tracked.id)}
                    style={{ width: '100%', height: '100%', margin: '5px' }}
                    src={tracked.image}
                  />
                )
              })}
          </div>
        </Card>

        <Card
          //This card contains the list of cameras that are connected
          bodyStyle={{ padding: '4px' }}
          headStyle={{ padding: 0 }}
          size="small"
          title={
            <h2 style={{ margin: '0px 8px', fontSize: '20px' }}>Cameras</h2>
          }
          extra={<PlusOutlined style={{ marginRight: 10 }} />}
        >
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))'
            }}
          >
            {sources &&
              sources.map((source) => {
                var iterator = 0
                return (
                  //Create a cameracard for each stream
                  <CameraCard
                    key={`cameraCard-${iterator++}`}
                    id={source.id}
                    title={source.name}
                    setSize={setPrimary}
                  />
                )
              })}
          </div>
        </Card>
      </div>

      <div style={{ overflowY: 'auto' }}>
        {sources && (
          //The grid contains all the videoplayers
          <Grid
            sources={sources}
            primary={primary ?? sources[0]?.id}
            setPrimary={(sourceId: string) => setPrimary(sourceId)}
            indicator={currentIndicator}
          />
        )}
      </div>
    </Layout.Content>
  )

  /** Placeholder to start tracking something. TODO: implement tracking */
  async function addSelection() {
    const pictures = ['car', 'guy', 'garden']
    const picture = pictures[Math.floor(Math.random() * pictures.length)]

    var result = await fetch(process.env.PUBLIC_URL + `/${picture}.png`)
    var blob = await result.blob()
    var reader = new FileReader()
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        setTracking(
          tracking.concat({
            id: selectionRef.current++,
            name: 'abc',
            image: reader.result,
            data: ''
          })
        )
      }
    }
    reader.readAsDataURL(blob)
  }

  /** Placeholder to stop tracking an object, TODO: implement tracking */
  function removeSelection(id: number) {
    setTracking(tracking.filter((tracked) => tracked.id !== id))
  }
}
