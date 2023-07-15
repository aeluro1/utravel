import { useState } from "react";
import { usePagination } from "react-instantsearch-hooks-web";


export default function Pagination(props) {
  const { activePage, setActivePage } = useState(1);
  const { pages } = usePagination(props);
  return (
    <Pagination
      value={activePage}
      onChange={setActivePage}
      total={props.totalPages}
      siblings={props.padding}
    />
  )
}