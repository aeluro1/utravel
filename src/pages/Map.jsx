import { createStyles } from "@mantine/core";
import GoogleMaps from "components/GoogleMaps";


const useStyles = createStyles((theme) => ({
  container: {
    width: "100%",
    height: "100%",
    display: "flex",
    flexFlow: "column nowrap",
    justifyContent: "center",
    alignItems: "center",
    background: "red"
  }
}));

export default function Map() {
  const { classes } = useStyles();
  return (
    <div className={classes.container}>
      <GoogleMaps />
    </div>
  );
}