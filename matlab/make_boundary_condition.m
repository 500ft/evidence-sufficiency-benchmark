function make_boundary_condition(csvPath, stem, S)
%MAKE_BOUNDARY_CONDITION Draw the six-panel boundary-condition figure.
%   Input: reports/evidence-sufficiency/boundary-condition-data.csv, written by
%   python -m studies.evidence_sufficiency.plot from results.json and spec.json.
%   Rows are panels (a)-(c) prescribed force and (d)-(f) prescribed
%   displacement; columns are stress, extension and reaction. Blue circles are
%   the control, orange squares the half-modulus artifact. A filled marker
%   means the panel's check passes against the reference; hollow means it fails.
%   Output: <stem>.png (300 dpi), <stem>.pdf and <stem>.svg (vector).

opts = detectImportOptions(csvPath, 'TextType', 'string', 'Delimiter', ',');
opts = setvartype(opts, {'panel', 'loading', 'load', 'observable', 'unit', 'variant', ...
    'label', 'check_passes'}, 'string');
opts = setvartype(opts, {'value', 'reference'}, 'double');
T = readtable(csvPath, opts);
assert(height(T) == 12, 'expected 12 plotted points, got %d', height(T));
assert(all(ismember(T.check_passes, ["true", "false"])), 'check_passes must be true/false');
pass = T.check_passes == "true";

letters  = 'abcdef';
obs      = ["stress", "displacement", "force"];
ylabels  = ["stress $\sigma$ (MPa)", "extension $\delta$ (mm)", "reaction $R$ (N)"];
loadings = ["force", "displacement"];
variants = ["correct_control", "modulus_fault"];
markers  = ['o', 's'];
colours  = [S.c.blue; S.c.orange];
xlim_    = [0.4 2.6];

fig = figure('Visible', 'off', 'Units', 'centimeters', 'Position', [2 2 18 10.6], ...
    'PaperPositionMode', 'auto');
tl = tiledlayout(fig, 2, 3, 'TileSpacing', 'compact', 'Padding', 'compact');

for i = 1:2
    for j = 1:3
        k = (i - 1) * 3 + j;
        ax = nexttile(tl, k); hold(ax, 'on');
        P = T(T.panel == letters(k), :);
        assert(height(P) == 2 && all(P.loading == loadings(i)) && all(P.observable == obs(j)), ...
            'panel %s rows do not match the expected loading and observable', letters(k));
        ref = unique(P.reference);
        assert(isscalar(ref), 'panel %s has more than one reference', letters(k));

        % equal limits within each observable, zero visible
        top = 1.25 * max(T.value(T.observable == obs(j)));
        step = nice_step(top / 4);
        set(ax, 'XLim', xlim_, 'YLim', [0 top], 'XTick', [1 2], 'YTick', 0:step:top);
        if obs(j) == "displacement"
            ax.YAxis.TickLabelFormat = '%.2f';
        end

        plot(ax, xlim_, [ref ref], ':', 'Color', S.c.grey, 'LineWidth', 1.0);
        for v = 1:2
            r = P(P.variant == variants(v), :);
            assert(height(r) == 1, 'panel %s: one %s row expected', letters(k), variants(v));
            face = 'w';
            if pass(T.panel == letters(k) & T.variant == variants(v))
                face = colours(v, :);
            end
            plot(ax, v, r.value, markers(v), 'MarkerSize', 7, 'LineWidth', 1.3, ...
                'MarkerEdgeColor', colours(v, :), 'MarkerFaceColor', face);
        end

        ylabel(ax, ylabels(j));
        if i == 2
            ax.XTickLabel = {'control', 'half modulus'};
        else
            ax.XTickLabel = {};
        end

        % panel letter as a left-aligned title; the loading goes in the first column
        title(ax, ['\textbf{' letters(k) '}'], 'FontSize', S.size.letter);
        if j == 1
            subtitle(ax, sprintf('prescribed %s, %s', loadings(i), P.load(1)), ...
                'FontSize', S.size.note, 'Color', S.c.ink);
        else
            subtitle(ax, '$\;$', 'FontSize', S.size.note);  % blank line keeps the letters aligned
        end
        ax.TitleHorizontalAlignment = 'left';

        % direct labels, each placed once
        if letters(k) == 'a'
            for v = 1:2
                r = P(P.variant == variants(v), :);
                text(ax, v, r.value + 0.09 * top, r.label, 'Color', colours(v, :), ...
                    'FontSize', S.size.label, 'HorizontalAlignment', 'center', ...
                    'VerticalAlignment', 'bottom');
            end
        elseif letters(k) == 'b'
            f = P(P.variant == variants(2), :);
            c = P(P.variant == variants(1), :);
            assert(~pass(T.panel == 'b' & T.variant == variants(2)) && ...
                pass(T.panel == 'b' & T.variant == variants(1)), ...
                'panel b notes assume a failing half modulus and a passing control');
            text(ax, 1.82, f.value, 'hollow: check fails', 'Color', S.c.ink, ...
                'FontSize', S.size.tick, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'middle');
            text(ax, 1, c.value - 0.1 * top, 'filled: check passes', 'Color', S.c.ink, ...
                'FontSize', S.size.tick, 'HorizontalAlignment', 'center', 'VerticalAlignment', 'top');
        elseif letters(k) == 'd'
            text(ax, xlim_(2), ref + 0.03 * top, 'specification reference', 'Color', S.c.grey, ...
                'FontSize', S.size.tick, 'HorizontalAlignment', 'right', 'VerticalAlignment', 'bottom');
        end
    end
end

print(fig, [stem '.svg'], '-dsvg', '-vector');
export_pair(fig, stem);
end

function s = nice_step(raw)
%NICE_STEP Smallest of 1, 2, 2.5 or 5 times a power of ten that is >= raw.
p = 10 ^ floor(log10(raw));
c = [1 2 2.5 5 10] * p;
s = c(find(c >= raw, 1));
end
