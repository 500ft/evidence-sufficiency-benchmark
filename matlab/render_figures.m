%RENDER_FIGURES Redraw the data figure and write the result tables of this repository.
%   Run from the repository root with MATLAB R2025b:
%     matlab -batch "addpath matlab; render_figures"
%   Reads only committed files under reports/. Writes
%     reports/evidence-sufficiency/boundary-condition.{png,pdf,svg}
%     reports/evidence-sufficiency/{outcomes,policies}-table.tex
%     reports/claim-sufficiency/{explanations,decisions}-table.tex
%   Typeset the .tex fragments to PDF and PNG as described in matlab/README.md.

root = fileparts(fileparts(mfilename('fullpath')));
es = fullfile(root, 'reports', 'evidence-sufficiency');
cs = fullfile(root, 'reports', 'claim-sufficiency');
S = fig_style();
failed = {};

try
    make_boundary_condition(fullfile(es, 'boundary-condition-data.csv'), ...
        fullfile(es, 'boundary-condition'), S);
    fprintf('wrote boundary-condition\n');
catch err
    failed{end + 1} = 'boundary-condition';
    fprintf('FAILED boundary-condition: %s\n', getReport(err, 'extended', 'hyperlinks', 'off'));
end

try
    make_result_tables(es, cs);
    fprintf('wrote result tables\n');
catch err
    failed{end + 1} = 'result tables';
    fprintf('FAILED result tables: %s\n', getReport(err, 'extended', 'hyperlinks', 'off'));
end

if ~isempty(failed)
    error('render_figures:failed', 'failed: %s', strjoin(failed, ', '));
end
