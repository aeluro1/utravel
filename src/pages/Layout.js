import { Outlet } from "react-router-dom"
import { Container } from "@mantine/core"
import Navbar from "components/Navbar"


export default function Layout() {
  return (
    <div>
      <Navbar />
      <Container>
        <Outlet />
      </Container>
    </div>
  )
}