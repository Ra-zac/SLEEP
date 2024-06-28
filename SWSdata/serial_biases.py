import pickle5 as p
import pickle
import pandas.core.internals
import pandas.core.internals.managers


path_to_protocol5 = 'Serial_biases_at_3seconds.pkl'

with open(path_to_protocol5, "rb") as fh:
    data = p.load(fh)

with open(path_to_protocol5, "wb") as f:
  # Pickle the 'labeled-data' dictionary using the highest protocol available.
    pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)