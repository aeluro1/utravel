import { Outlet } from "react-router-dom"
import Navbar, { HEADER_HEIGHT } from "components/Navbar"
import { Space } from "@mantine/core"


export default function Layout() {
  return (
    <>
      <Navbar />
      <Space h={HEADER_HEIGHT} />
      <Outlet />
    </>
  )
}