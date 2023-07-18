import { Status, Wrapper } from "@googlemaps/react-wrapper";
import { Alert, LoadingOverlay, createStyles } from "@mantine/core";
import { useEffect, useRef } from "react";


const useStyles = createStyles((theme) => ({
  map: {
    width: "100%",
    height: "100%"
  },
  error: {
    width: "300px",
    height: "min-content"
  }
}));

function MapLoading() {
  return (
    <LoadingOverlay visible={true} overlayBlur={2} />
  );
}

function MapError() {
  const { classes } = useStyles();
  return (
    <Alert
      title="Error"
      color="red"
      className={classes.error}
    >
      Unable to load Google Maps.
    </Alert>
  );
}

function Map({ center, zoom }) {
  const { classes } = useStyles();
  const ref = useRef();
  useEffect(() => {
    new window.google.maps.Map(ref.current, { center, zoom });
  });
  return (
    <div ref={ref} id="map" className={classes.map} />
  );
}

const render = (status) => {
  if (status === Status.LOADING) return <MapLoading />;
  if (status === Status.FAILURE) return <MapError />;
  return null;
};

export default function GoogleMaps() {
  let center = { lat: -34.397, lng: 150.644 };
  let zoom = 4;
  return (
    <Wrapper
      apiKey={process.env.REACT_APP_GMAP_API_KEY}
      render={render}
    >
      <Map center={center} zoom={zoom} />
    </Wrapper>
  );
}