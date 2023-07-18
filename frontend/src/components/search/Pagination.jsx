import { useState } from "react";
import { Pagination } from "@mantine/core";
import { usePagination } from "react-instantsearch-hooks-web";


export default function SearchPagination(props) {
  const [activePage, setActivePage] = useState(1);
  const { nbPages, refine } = usePagination();
  const gotoPage = (p) => {
    console.log(nbPages);
    refine(p - 1);
    setActivePage(p);
  };

  return (
    <Pagination
      value={activePage}
      onChange={gotoPage}
      total={nbPages}
      {...props}
    />
  );
}