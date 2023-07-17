import { useContext } from "react";
import { Link } from "react-router-dom";
import { Button, Paper, Text, createStyles } from "@mantine/core";
import Table from "components/Table";
import TableEntry from "components/TableEntry";
import { savedItemsContext } from "contexts/SavedItemsContext";


const useStyles = createStyles((theme) => ({
  container: {
    height: "100%",
    width: "100%",
    padding: [theme.spacing.lg],
    display: "flex",
    flexFlow: "column nowrap"
  },
  paper: {
    width: "min(600px, 80%)",
    height: "300px",
    margin: "auto",
    display: "flex",
    flexFlow: "column nowrap",
    justifyContent: "center",
    alignItems: "center",
    gap: [theme.spacing.lg]
  }
}))

export default function Home() {
  const { savedItems } = useContext(savedItemsContext);
  const { classes } = useStyles();
  return (
    <div className={classes.container}>
      {savedItems.length === 0 ? (
        <Paper className={classes.paper} p="lg" shadow="md" withBorder>
          <Text ta="center">No items saved. Head over and find some attractions!</Text>
          <Link to="/browser"><Button>Browser</Button></Link>
        </Paper>
      ) : (
        <Table>
          {savedItems.map((h) => <TableEntry key={h.id} item={h} />)}
        </Table>
      )}
    </div>
  )
}

