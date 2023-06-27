import { Outlet, Link } from "react-router-dom"

export default function Layout() {
  return (
    <div>
      <p><Link to="/map">Map</Link></p>
      <Outlet />
    </div>
  )
}