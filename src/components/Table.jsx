import { createStyles } from "@mantine/core";


const useStyles = createStyles((theme) => ({
  results: {
    width: "100%",
    display: "grid",
    gap: [theme.spacing.sm],
    justifyItems: "center",
    [theme.fn.largerThan("sm")]: {
      gridTemplateColumns: "repeat(auto-fit, minmax(min(450px, 100%), 1fr))"
    },
    [theme.fn.smallerThan("sm")]: {
      gridTemplateColumns: "repeat(auto-fit, minmax(min(250px, 100%), 1fr))"
    },
  }
}))

export default function Table(props) {
  const { classes } = useStyles();

  // let items = axios.get();
 
  return (
    <div className={classes.results}>
      {props.children}
    </div>
  )
}