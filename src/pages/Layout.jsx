import { Outlet } from "react-router-dom"
import { createStyles } from "@mantine/core"
import Navbar, { HEADER_HEIGHT } from "components/Navbar"


const useStyles = createStyles((theme) => ({
  layout: {
    paddingTop: HEADER_HEIGHT,
    minHeight: "100vh",
    height: "100vh"
  }
}))

export default function Layout() {
  const { classes } = useStyles();
  return (
    <>
      <Navbar />
      <div className={classes.layout}>
        <Outlet />
      </div>
    </>
  )
}