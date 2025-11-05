use numpy::{PyArray1, PyReadonlyArray1};
use pyo3::prelude::*;
use rayon::prelude::*;

#[pyfunction]
#[pyo3(signature = (value, mn, mx, down_count))]
fn down_sample(
    py: Python,
    value: PyReadonlyArray1<f64>,
    mn: usize,
    mx: usize,
    down_count: usize,
) -> PyResult<(PyObject, PyObject)> {
    let value = value.as_slice()?;
    let len = value.len();

    // Clamp mn and mx to valid range
    let mn = mn.min(len);
    let mx = mx.min(len).max(mn);

    if mn >= mx || down_count == 0 {
        let empty_i32 = PyArray1::<i32>::zeros(py, [0], false).into();
        let empty_f64 = PyArray1::<f64>::zeros(py, [0], false).into();
        return Ok((empty_i32, empty_f64));
    }

    let _value = &value[mn..mx];
    let _index: Vec<i32> = (mn as i32..mx as i32).collect();
    let total_len = mx - mn;

    // Compute window size (at least 1)
    let window_size = (total_len as f64 / down_count as f64).max(1.0) as usize;
    let sample_count = total_len / window_size;

    if sample_count == 0 {
        let empty_i32 = PyArray1::<i32>::zeros(py, [0], false).into();
        let empty_f64 = PyArray1::<f64>::zeros(py, [0], false).into();
        return Ok((empty_i32, empty_f64));
    }

    // Parallel processing: split sample range across threads
    let num_threads = rayon::current_num_threads();
    let chunk_size = (sample_count + num_threads - 1) / num_threads;

    let results: Vec<_> = (0..num_threads)
        .into_par_iter()
        .map(|thread_id| {
            let start_sample = thread_id * chunk_size;
            let end_sample = (start_sample + chunk_size).min(sample_count);

            if start_sample >= end_sample {
                return (Vec::<i32>::new(), Vec::<f64>::new());
            }

            let mut down_index = Vec::with_capacity((end_sample - start_sample) * 2);
            let mut down_value = Vec::with_capacity((end_sample - start_sample) * 2);

            for i in start_sample..end_sample {
                let start = i * window_size;
                let end = (start + window_size).min(_value.len());
                if start >= end {
                    continue;
                }
                let window = &_value[start..end];

                let max_val = window.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));
                let min_val = window.iter().fold(f64::INFINITY, |a, &b| a.min(b));

                let idx = _index[start];
                down_index.push(idx);
                down_index.push(idx);
                down_value.push(max_val);
                down_value.push(min_val);
            }

            (down_index, down_value)
        })
        .collect();

    // Merge results
    let mut final_index = Vec::new();
    let mut final_value = Vec::new();
    for (idx, val) in results {
        final_index.extend(idx);
        final_value.extend(val);
    }

    // Convert to NumPy arrays
    let index_array = PyArray1::from_vec(py, final_index).into();
    let value_array = PyArray1::from_vec(py, final_value).into();

    Ok((index_array, value_array))
}

#[pymodule]
fn cracknuts_ext(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(down_sample, m)?)?;
    Ok(())
}
