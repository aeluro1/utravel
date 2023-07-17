import Table from "components/Table";
import TableEntry from "components/TableEntry";
import { useHits } from "react-instantsearch-hooks-web";


export default function Hits(props) {
  const { hits } = useHits(props);
  return (
    <Table>
      {hits.map((h) => <TableEntry key={h.id} item={h} />)}
    </Table>
  );
}