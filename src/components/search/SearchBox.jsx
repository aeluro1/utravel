import { Input } from "@mantine/core"
import { useSearchBox } from "react-instantsearch-hooks-web"


let timerId;
const queryHook = (query, search) => {
  clearTimeout(timerId);
  timerId = setTimeout(() => search(query), 100);
}

export default function SearchBox(props) {
  const { refine } = useSearchBox({ ...props, queryHook });
  const search = (q) => {
    refine(q);
  }

  return (
      <Input
        onChange={(e) => search(e.target.value)}
        { ...props }
      />
  )
}