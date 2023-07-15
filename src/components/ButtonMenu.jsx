import { Menu } from "@mantine/core";


export default function ButtonMenu() {
  return (
    <Menu
      transitionProps={{ transition: "pop-top-right" }}
      position="bottom-end"
    ></Menu>
  )
}