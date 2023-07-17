import { Outlet } from "react-router-dom";
import { createStyles } from "@mantine/core";
import Navbar, { HEADER_HEIGHT } from "components/Navbar";


const useStyles = createStyles((theme) => ({
  layout: {
    paddingTop: HEADER_HEIGHT,
    minHeight: "100vh",
    height: "100vh",
    backgroundColor: [theme.colorScheme === "dark" ? theme.colors.dark[8] : theme.colors.gray[0]]
  }
}));

export default function Layout() {
  const { classes } = useStyles();
  return (
    <>
      <Navbar />
      <div className={classes.layout}>
        <Outlet />
      </div>
    </>
  );
}